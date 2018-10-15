from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework.response import Response
from serializers import UserSerializer, GroupSerializer, KNNNodeSerializer

from osmmanager import OsmManager
from model_less import KNNNode

import requests


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


class KNNNodeViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = KNNNodeSerializer

    def get_queryset(self):
        longitude = self.request.query_params.get('longitude')
        latitude = self.request.query_params.get('latitude')
        k = self.request.query_params.get('k')
        queryset = OsmManager().get_knn(longitude, latitude, k)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        knn_nodes = []
        for node in queryset:
            knn_node = KNNNode(**node)
            knn_nodes.append(knn_node)
        serializer = KNNNodeSerializer(instance=knn_nodes, many=True)
        return Response(serializer.data)
