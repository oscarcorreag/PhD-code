# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import numpy as np

from django.contrib.auth.models import User
from django.db import transaction
from django.db.utils import DatabaseError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

import models
import exceptions
import serializers
import osmmanager
import suitability
from tasks import compute_plan
# import vst_rs
# from link_performance import identity

# import logging


# logger = logging.getLogger("django")

MIN_DIST = 200


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = serializers.UserSerializer


class SessionViewSet(viewsets.ModelViewSet):

    queryset = models.Session.objects.all().order_by("-start_time")
    serializer_class = serializers.SessionSerializer

    @staticmethod
    def active_exists():
        # Is there active sessions?
        active_session = None
        try:
            active_session = models.Session.objects.get(active=True)
        except models.Session.DoesNotExist:
            pass
        return active_session

    @staticmethod
    def generate_graph(city, seed=None, delta_meters=5000):
        # Compute random bbox coordinates based on session's city.
        if seed is not None:
            np.random.seed(seed)
        bounds = models.CITY_BOUNDS[city]
        delta = delta_meters / 111111.
        min_lon = np.random.uniform(bounds[0], bounds[2] - delta)
        min_lat = np.random.uniform(bounds[1], bounds[3] - delta)
        max_lon = min_lon + delta
        max_lat = min_lat + delta
        # Generate network sample.
        osm = osmmanager.OsmManager()
        generator = suitability.SuitableNodeWeightGenerator()
        graph, hotspots, pois, _, _ = osm.generate_graph_for_bbox(min_lon, min_lat, max_lon, max_lat, generator)
        return graph, hotspots, pois, min_lon, min_lat, max_lon, max_lat

    @staticmethod
    def simulate_queries(how_many, graph, available, pois, seed=None):
        # Group POIs by subtype (activity).
        pois_per_activity = dict()
        for p in pois:
            pois_per_activity.setdefault(graph[p][2]['subtype'], []).append(p)
        # Create queries.
        if seed is not None:
            np.random.seed(seed)
        queries = []
        occupied = set()
        nq = len(pois_per_activity.keys())
        nuq = how_many / nq
        for i, (activity, pois_) in enumerate(pois_per_activity.iteritems()):
            where = set(available).difference(occupied)
            nuq_ = nuq
            if i == nq - 1:
                nuq_ = how_many - (nq - 1) * nuq
            origins = np.random.choice(a=list(where), size=nuq_, replace=False)
            queries.append((origins, pois_, activity))
            occupied.update(origins)
        return queries

    @staticmethod
    def prepare_new(simulated_users, city, seed=None):
        edges = list()
        nodes = list()
        users = list()
        activities = list()
        # Generate graph associated with session.
        graph, hotspots, pois, min_lon, min_lat, max_lon, max_lat = SessionViewSet.generate_graph(city, seed=seed)
        # Are there hot-spots, POIs?
        if not hotspots:
            raise exceptions.NoHotspotsException
        if not pois:
            raise exceptions.NoPoisException
        # Are there available nodes for users? (take into account creator)
        available = set(graph.keys()).difference(hotspots).difference(pois)
        if len(available) < simulated_users + 1:
            raise exceptions.NoAvailableNodesException
        # Choose a random origin for creator.
        np.random.seed(seed)
        origin_creator = np.random.choice(a=list(available), size=1, replace=False)[0]
        available.remove(origin_creator)
        # Create SessionGraphEdge objects.
        for (i, j), weight in graph.get_edges().iteritems():
            edges.append(models.SessionGraphEdge(node_i=i, node_j=j, weight=weight))
        # Create SessionGraphNode objects.
        for hotspot in hotspots:
            nodes.append(models.SessionGraphNode(node=hotspot, node_type='H'))
        for node in available:
            nodes.append(models.SessionGraphNode(node=node, node_type='N'))
        # Simulate queries
        queries = SessionViewSet.simulate_queries(simulated_users, graph, available, pois)
        for origins, pois_, activity in queries:
            # Create SessionUser objects.
            for origin in origins:
                users.append(models.SessionUser(origin=origin, activity=activity))
            # Append POIs to SessionGraphNode objects.
            for poi in pois_:
                nodes.append(models.SessionGraphNode(node=poi, node_type='P', activity=activity))
            # Create SessionActivity objects.
            activities.append(models.SessionActivity(activity=activity))
        # return session, edges, nodes, users, activities
        return edges, nodes, users, activities, min_lon, min_lat, max_lon, max_lat, origin_creator

    # @staticmethod
    # def build_graph_from_model(session_id):
    #     graph = suitability.SuitabilityDigraph(capacitated=True)
    #     generator = suitability.SuitableNodeWeightGenerator()
    #     default_node_weight = generator.weights["FORGET_IT"]
    #     hotspot_weight = generator.weights["VERY_SUITABLE"]
    #     # Retrieve edges from the DB for this session.
    #     # Append edge by edge to the new graph.
    #     # Nodes' weights are initialized.
    #     session_edges = models.SessionGraphEdge.objects.filter(session__id=session_id)
    #     for session_edge in session_edges:
    #         edge = (session_edge.node_i, session_edge.node_j)
    #         graph.append_edge_2(edge,
    #                             session_edge.weight,
    #                             nodes_weights=(default_node_weight, default_node_weight),
    #                             capacity=1.0,
    #                             check_exists=False)
    #     # Hot-spots' weights have to be updated.
    #     # Therefore, hot-spots are retrieved from DB for this session.
    #     hotspots = models.SessionGraphNode.objects.filter(session__id=session_id, node_type="H")
    #     node_weights = {hotspot.node: hotspot_weight for hotspot in hotspots}
    #     graph.update_node_weights(node_weights)
    #     return graph

    # @staticmethod
    # def build_queries_from_model(session_id):
    #     # Retrieve users and POIs for this session.
    #     session_users = models.SessionUser.objects.filter(session__id=session_id)
    #     pois = models.SessionGraphNode.objects.filter(session__id=session_id)
    #     # Create dictionaries of users and POIs per activity.
    #     users_per_activity = dict()
    #     for session_user in session_users:
    #         users_per_activity.setdefault(session_user.activity, []).append(session_user.origin)
    #     pois_per_activity = dict()
    #     for poi in pois:
    #         pois_per_activity.setdefault(poi.activity, []).append(poi.node)
    #     # Merge both dictionaries into the queries
    #     queries = [(users, pois_per_activity[activity]) for activity, users in users_per_activity.iteritems()]
    #     return queries

    # @staticmethod
    # def compute_plan(session_id):
    #     # Build graph and queries for this session.
    #     graph = SessionViewSet.build_graph_from_model(session_id)
    #     queries = SessionViewSet.build_queries_from_model(session_id)
    #     # Compute plan
    #     vstrs = vst_rs.VST_RS(graph)
    #     plans, c, _, _, _, _, _ = vstrs.non_congestion_aware(queries, 4, 8, identity, merge_users=False, verbose=True)
    #     print plans, c

    @action(detail=False)
    def can_create(self, request):
        # Check whether an active session exists already.
        if SessionViewSet.active_exists():
            raise exceptions.ActiveSessionExistsException
        return Response({"status_code": status.HTTP_200_OK, "detail": "A new session can be created."},
                        status=status.HTTP_200_OK)

    # @action(detail=False)
    # def can_end(self, request):

    def perform_create(self, serializer):
        # Check whether an active session exists already.
        if SessionViewSet.active_exists():
            raise exceptions.ActiveSessionExistsException
        # Prepare new session: create detail objects for the new session.
        simulated_users = serializer.validated_data["simulated_users"]
        city = serializer.validated_data["city"]
        edges, nodes, users, activities, min_lon, min_lat, max_lon, max_lat, origin_creator = \
            SessionViewSet.prepare_new(simulated_users, city)
        # Save session and its details within a database transaction.
        try:
            with transaction.atomic():
                session = serializer.save(
                    active=True,
                    min_lon=min_lon,
                    min_lat=min_lat,
                    max_lon=max_lon,
                    max_lat=max_lat)
                # Save graph edges
                for edge in edges:
                    edge.session = session
                    edge.save()
                # Save nodes.
                for node in nodes:
                    node.session = session
                    node.save()
                # Save users.
                users.append(models.SessionUser(origin=origin_creator, user=session.creator))
                for user in users:
                    user.session = session
                    user.save()
                # Save activities.
                for activity in activities:
                    activity.session = session
                    activity.save()
        except DatabaseError:
            raise exceptions.NewSessionTransactionException

    @action(detail=False, methods=["post"])
    def join(self, request):
        # Retrieve the active session.
        active_session = SessionViewSet.active_exists()
        if not active_session:
            raise exceptions.NoActiveSessionExistsException
        serializer = self.get_serializer(active_session)
        # Get real users already in the session.
        real_session_users = models.SessionUser.objects.filter(user__isnull=False)
        # If the user who made the request is NOT in the session already AND the number of real users has been reached,
        # the user is NOT allowed to join the session.
        new_user_id = int(request.query_params["user"])
        ids = {u.user.id for u in real_session_users}
        joined_before = new_user_id in ids
        if not joined_before and active_session.real_users == len(real_session_users):
            raise exceptions.NotAllowedToJoinSessionException
        # If the user who made the request is NOT in the session already, SessionUser object corresponding to this user
        # is created.
        if not joined_before:
            # Retrieve the User object that will be set as FK.
            new_user = User.objects.get(pk=new_user_id)
            # There must be at least one real user. Choose the first one.
            chosen_session_user = real_session_users[0]
            osm = osmmanager.OsmManager()
            coords = osm.get_coordinates(chosen_session_user.origin)
            # Origin of this new session user is close (>= MIN_DIST) to the chosen one but it is different from other
            # real users' origins.
            knn = osm.get_knn(coords["longitude"], coords["latitude"], len(real_session_users), MIN_DIST)
            origins = {u.origin for u in real_session_users}
            knn_ = {nn["node"] for nn in knn}
            temp = list(knn_.difference(origins))
            assert len(temp) == 1
            new_session_user = models.SessionUser(origin=temp[0], user=new_user, session=active_session)
            new_session_user.save()
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def plan(self, request, pk):
        session = self.get_object()
        # Update user is ready to travel.
        user_id = int(request.query_params["user"])
        activity = request.query_params["activity"]
        session_user = models.SessionUser.objects.get(session=session, user__id=user_id)
        session_user.ready_to_travel = True
        session_user.activity = activity
        session_user.save()
        # Am I the last user who issue the request to compute the plan?
        users_ready = models.SessionUser.objects.filter(ready_to_travel=True)
        if len(users_ready) < session.real_users:
            return Response({"status_code": 100, "detail": "You must wait till all users are ready to travel."},
                            status=status.HTTP_100_CONTINUE)
        compute_plan(session)
        return Response({"status_code": 200, "detail": "You will be sent a notification with your plan details"},
                        status=status.HTTP_200_OK)


class SessionActivityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.SessionActivitySerializer

    def get_queryset(self):
        session_id = self.kwargs["session"]
        return models.SessionActivity.objects.filter(session__id=session_id).order_by("activity")


def session_user_from_record(record):
    session_user = models.SessionUser(**record)
    session_user.user = User(id=record["user_id"])
    # These two lines are needed as in the constructor, the properties are NOT called.
    session_user.longitude = record["longitude"]
    session_user.latitude = record["latitude"]
    return session_user


class SessionUserViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.SessionUserSerializer

    def get_object(self):
        session_id = self.kwargs["session"]
        user_id = self.kwargs["pk"]
        # queryset = OsmManager().get_session_user_by_pk(user_id)
        record = osmmanager.OsmManager().get_session_user(session_id, user_id)
        if not record:
            raise exceptions.NoSessionUserException
        session_user = session_user_from_record(record)
        session_user.session = models.Session(id=session_id)
        return session_user

    def get_queryset(self):
        session_id = self.kwargs["session"]
        res = osmmanager.OsmManager().get_session_users(session_id)
        session_users = []
        for record in res:
            session_user = session_user_from_record(record)
            session_user.session = models.Session(id=session_id)
            session_users.append(session_user)
        return session_users


def session_node_from_record(record):
    session_node = models.SessionGraphNode(**record)
    # These two lines are needed as in the constructor, the properties are NOT called.
    session_node.longitude = record["longitude"]
    session_node.latitude = record["latitude"]
    return session_node


class SessionGraphNodeViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.SessionGraphNodeSerializer

    def get_queryset(self):
        session_id = self.kwargs["session"]
        type_ = self.request.query_params["type"]
        activity = None
        if self.request.query_params.has_key("activity"):
            activity = self.request.query_params["activity"]
        res = osmmanager.OsmManager().get_session_nodes(session_id, type_, activity)
        session_nodes = []
        for record in res:
            session_node = session_node_from_record(record)
            session_node.session = models.Session(id=session_id)
            session_nodes.append(session_node)
        return session_nodes
