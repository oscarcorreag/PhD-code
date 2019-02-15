# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class Session(models.Model):
    active = models.BooleanField(default=False)
    min_lon = models.FloatField()
    min_lat = models.FloatField()
    max_lon = models.FloatField()
    max_lat = models.FloatField()
    travel_cost = models.FloatField(null=True)


class SessionGraphEdge(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    node_i = models.BigIntegerField()
    node_j = models.BigIntegerField()
    weight = models.FloatField()


class SessionGraphNode(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    node = models.BigIntegerField()
    node_type = models.CharField(max_length=1)
    activity = models.CharField(max_length=50, null=True)

    def __init__(self, *args, **kwargs):
        super(SessionGraphNode, self).__init__(*args, **kwargs)
        self._longitude = 0.0
        self._latitude = 0.0

    def get_longitude(self):
        return self._longitude

    def set_longitude(self, value):
        self._longitude = value

    def get_latitude(self):
        return self._latitude

    def set_latitude(self, value):
        self._latitude = value

    longitude = property(get_longitude, set_longitude)
    latitude = property(get_latitude, set_latitude)