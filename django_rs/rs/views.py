# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import transaction
from django.db.utils import DatabaseError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from controllers import SessionController
from model_less import KnnNode
from models import Session, SessionActivity, SessionUser
from osmmanager import OsmManager
from rs.exceptions import ActiveSessionExistsException, NewSessionTransactionException, NoActiveSessionExistsException, \
    NotAllowedToJoinSessionException, NoSessionUserException
from serializers import UserSerializer, KnnNodeSerializer, SessionSerializer, SessionActivitySerializer, \
    SessionUserSerializer

# import logging


# logger = logging.getLogger("django")

MIN_DIST = 200


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer


# class GroupViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer


class KnnNodeViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = KnnNodeSerializer

    def get_queryset(self):
        longitude = self.request.query_params.get("longitude")
        latitude = self.request.query_params.get("latitude")
        k = self.request.query_params.get("k")
        return OsmManager().get_knn(longitude, latitude, k)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # TODO: This should be within get_queryset(self)
        knn_nodes = []
        for node in queryset:
            knn_node = KnnNode(**node)
            knn_nodes.append(knn_node)
        serializer = KnnNodeSerializer(instance=knn_nodes, many=True)
        return Response(serializer.data)


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all().order_by("-start_time")
    serializer_class = SessionSerializer

    @action(detail=False)
    def can_create(self, request):
        # Check whether an active session exists already.
        if SessionController.active_exists():
            # logger.error(ActiveSessionExistsException.default_detail)
            raise ActiveSessionExistsException
        return Response({"status_code": status.HTTP_200_OK, "detail": "A new session can be created."}, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        # Check whether an active session exists already.
        if SessionController.active_exists():
            # logger.error(ActiveSessionExistsException.default_detail)
            raise ActiveSessionExistsException
        # Prepare new session: create detail objects for the new session.
        simulated_users = serializer.validated_data["simulated_users"]
        city = serializer.validated_data["city"]
        edges, nodes, users, activities, min_lon, min_lat, max_lon, max_lat, origin_creator = \
            SessionController.prepare_new(simulated_users, city)
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
                users.append(SessionUser(origin=origin_creator, user=session.creator))
                for user in users:
                    user.session = session
                    user.save()
                # Save activities.
                for activity in activities:
                    activity.session = session
                    activity.save()
        except DatabaseError:
            raise NewSessionTransactionException

    @action(detail=False, methods=["post"])
    def join(self, request):
        # Retrieve the active session.
        try:
            active_session = Session.objects.get(active=True)
        except Session.DoesNotExist:
            raise NoActiveSessionExistsException
        serializer = self.get_serializer(active_session)
        # Get real users already in the session.
        real_session_users = SessionUser.objects.filter(user__isnull=False)
        # If the user who made the request is NOT in the session already AND the number of real users has been reached,
        # the user is NOT allowed to join the session.
        new_user_id = int(request.query_params["user"])
        ids = {u.user.id for u in real_session_users}
        joined_before = new_user_id in ids
        if not joined_before and active_session.real_users == len(real_session_users):
            raise NotAllowedToJoinSessionException
        # If the user who made the request is NOT in the session already, SessionUser object corresponding to this user
        # is created.
        if not joined_before:
            # Retrieve the User object that will be set as FK.
            new_user = User.objects.get(pk=new_user_id)
            # There must be at least one real user. Choose the first one.
            chosen_session_user = real_session_users[0]
            osm = OsmManager()
            coords = osm.get_coordinates(chosen_session_user.origin)
            # Origin of this new session user is close (>= MIN_DIST) to the chosen one but it is different from other
            # real users' origins.
            knn = osm.get_knn(coords["longitude"], coords["latitude"], len(real_session_users), MIN_DIST)
            origins = {u.origin for u in real_session_users}
            knn_ = {nn["node"] for nn in knn}
            temp = list(knn_.difference(origins))
            assert len(temp) == 1
            new_session_user = SessionUser(origin=temp[0], user=new_user, session=active_session)
            new_session_user.save()
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def plan(self, request):
        session = self.get_object()
        # Update user is ready to travel.
        user_id = int(request.query_params["user"])
        activity = request.query_params["activity"]
        session_user = SessionUser.objects.get(session=session, user__id=user_id)
        session_user.save(ready_to_travel=True, activity=activity)
        # Am I the last user who issue the request to compute the plan?
        users_ready = SessionUser.objects.filter(ready_to_travel=True)
        if len(users_ready) < session.real_users:
            return Response({"status_code": 100, "detail": "You must wait till all users are ready to travel."})
        return Response({"status_code": 200, "detail": "OK"})


class SessionActivityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SessionActivitySerializer

    def get_queryset(self):
        session_id = self.kwargs["session"]
        return SessionActivity.objects.filter(session__id=session_id)


def session_user_from_record(record):
    session_user = SessionUser(**record)
    session_user.user = User(id=record["user_id"])
    session_user.longitude = record["longitude"]
    session_user.latitude = record["latitude"]
    return session_user


class SessionUserViewSet(viewsets.ModelViewSet):
    serializer_class = SessionUserSerializer

    def get_object(self):
        session_id = self.kwargs["session"]
        user_id = self.kwargs["pk"]
        # queryset = OsmManager().get_session_user_by_pk(user_id)
        record = OsmManager().get_session_user(session_id, user_id)
        if not record:
            raise NoSessionUserException
        session_user = session_user_from_record(record)
        session_user.session = Session(id=session_id)
        return session_user

    def get_queryset(self):
        session_id = self.kwargs["session"]
        res = OsmManager().get_session_users(session_id)
        session_users = []
        for user in res:
            session_user = session_user_from_record(user)
            session_user.session = Session(id=session_id)
            session_users.append(session_user)
        return session_users

