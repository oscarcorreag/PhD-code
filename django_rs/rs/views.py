# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import transaction
from django.db.utils import DatabaseError
from rest_framework.response import Response
from rest_framework import viewsets, status

from django.contrib.auth.models import User, Group
from models import Session, SessionUser
from model_less import KnnNode
from rs.exceptions import NotEnoughNodesException, ActiveSessionExistsException, NewSessionTransactionException

from serializers import UserSerializer, GroupSerializer, KnnNodeSerializer, SessionSerializer

from osmmanager import OsmManager

from controllers import SessionController

# import logging


# logger = logging.getLogger('django')


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


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
        # Get the session object to associate it with its corresponding details.
        session = Session(**serializer.validated_data)
        session.active = True
        # Prepare new session: create detail objects for the new session.
        graph_model, pois_model, hotspots_model, users_model = SessionController.prepare_new(session)
        # It may happen the sample yields no graph nodes.
        if len(graph_model) == 0 or len(pois_model) == 0 or len(hotspots_model) == 0 or len(users_model) == 0:
            # logger.error(NotEnoughNodesException.default_detail)
            raise NotEnoughNodesException
        try:
            with transaction.atomic():
                session.save()
                # Save graph.
                for edge_model in graph_model:
                    edge_model.session = session
                    edge_model.save()
                # Save POIs.
                for poi_model in pois_model:
                    poi_model.session = session
                    poi_model.save()
                # Save hot-spots.
                for hotspot_model in hotspots_model:
                    hotspot_model.session = session
                    hotspot_model.save()
                # Save users.
                for user_model in users_model:
                    user_model.session = session
                    user_model.save()
        except DatabaseError:
            raise NewSessionTransactionException
        return Response(session, status=status.HTTP_201_CREATED)
