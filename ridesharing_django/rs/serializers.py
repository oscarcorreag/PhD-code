from rest_framework import serializers
from django.contrib.auth.models import User, Group
from models import Session


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


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
        model = Session
        fields = ('start_time', 'end_time', 'city', 'current', 'creator', 'real_users', 'simulated_users')
