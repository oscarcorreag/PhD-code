from rest_framework import serializers
from django.contrib.auth.models import User, Group
from models import Session, SessionActivity


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'url', 'username', 'email')


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
        fields = ('id', 'start_time', 'end_time', 'city', 'active', 'creator', 'real_users', 'simulated_users')


class SessionActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionActivity
        fields = ('activity',)
