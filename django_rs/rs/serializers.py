from rest_framework import serializers
from django.contrib.auth.models import User, Group

import models


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ("id", "url", "username", "email")


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ("url", "name")


class KnnNodeSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    node = serializers.IntegerField(read_only=True)
    longitude = serializers.FloatField(read_only=True)
    latitude = serializers.FloatField(read_only=True)
    distance = serializers.FloatField(read_only=True)


class SessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Session
        fields = ("id",
                  "start_time",
                  "end_time",
                  "city",
                  "active",
                  "creator",
                  "real_users",
                  "simulated_users",
                  "min_lon",
                  "min_lat",
                  "max_lon",
                  "max_lat",
                  "travel_cost", )


class SessionActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SessionActivity
        fields = ("session", "activity",)


class SessionUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SessionUser
        fields = ("id",
                  "session",
                  "user",
                  "join_time",
                  "origin",
                  "destination",
                  "activity",
                  "ready_to_travel",
                  "longitude",
                  "latitude")


class SessionGraphNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SessionGraphNode
        fields = ("id", "session", "node", "node_type", "activity", "longitude", "latitude")


class SessionPlanVehicleRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SessionPlanVehicleRoute
        fields = ("id",
                  "node_i",
                  "node_i_longitude",
                  "node_i_latitude",
                  "node_j",
                  "node_j_longitude",
                  "node_j_latitude",
                  "vehicle_id")
