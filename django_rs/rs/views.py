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
    NotAllowedToJoinSessionException
from serializers import UserSerializer, KnnNodeSerializer, SessionSerializer, SessionActivitySerializer

# import logging


# logger = logging.getLogger('django')

MIN_DIST = 200


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
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
        longitude = self.request.query_params.get('longitude')
        latitude = self.request.query_params.get('latitude')
        k = self.request.query_params.get('k')
        return OsmManager().get_knn(longitude, latitude, k)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        knn_nodes = []
        for node in queryset:
            knn_node = KnnNode(**node)
            knn_nodes.append(knn_node)
        serializer = KnnNodeSerializer(instance=knn_nodes, many=True)
        return Response(serializer.data)


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all().order_by('-start_time')
    serializer_class = SessionSerializer

    def perform_create(self, serializer):
        # Check whether an active session exists already.
        if SessionController.active_exists():
            # logger.error(ActiveSessionExistsException.default_detail)
            raise ActiveSessionExistsException
        # Prepare new session: create detail objects for the new session.
        simulated_users = serializer.validated_data['simulated_users']
        city = serializer.validated_data['city']
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

    @action(detail=False, methods=['post'])
    def join(self, request):
        # Retrieve the active session.
        queryset = Session.objects.filter(active=True)
        if not queryset:
            raise NoActiveSessionExistsException
        active_session = queryset[0]
        serializer = self.get_serializer(active_session)
        # Get real users already in the session.
        real_session_users = SessionUser.objects.filter(user__isnull=False)
        # If the user who made the request is NOT in the session already AND the number of real users has been reached,
        # the user is NOT allowed to join the session.
        user_id = int(request.query_params["user"])
        joined_before = False
        for u in real_session_users:
            if u.user.id == user_id:
                joined_before = True
        if not joined_before and active_session.real_users == len(real_session_users):
            raise NotAllowedToJoinSessionException
        # If the user who made the request is NOT in the session already, SessionUser object corresponding to this user
        # is created.
        if not joined_before:
            other_user = User.objects.get(pk=user_id)
            # There must be at least one real user. Choose the first one.
            real_user = real_session_users[0]
            osm = OsmManager()
            coords = osm.get_coordinates(real_user.origin)
            # Origin of this new session user is close (>= MIN_DIST) to the chosen one.
            one_nn = osm.get_knn(coords["longitude"], coords["latitude"], 1, MIN_DIST)[0]
            other_user = SessionUser(origin=one_nn['node'], user=other_user, session=active_session)
            other_user.save()
        return Response(serializer.data)


class SessionActivityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SessionActivitySerializer

    def get_queryset(self):
        session = self.kwargs['session']
        return SessionActivity.objects.filter(session__id=session)
