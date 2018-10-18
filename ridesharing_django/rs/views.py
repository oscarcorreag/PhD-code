# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.response import Response
from rest_framework import viewsets

from django.contrib.auth.models import User, Group
from models import Session
from model_less import KnnNode

from serializers import UserSerializer, GroupSerializer, KnnNodeSerializer, SessionSerializer

from osmmanager import OsmManager


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
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
