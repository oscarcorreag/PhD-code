# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

CITIES = (
    ('MEL', 'Melbourne'),
    ('MHK', 'Manhattan'),
    ('UIO', 'Quito'),
)

CITY_BOUNDS = {
    'MEL': [144.58265438867193, -38.19424168942873, 145.36955014062505, -37.55250095415727],
    'MHK': [-74.0326191484375, 40.69502239217181, -73.93236890429688, 40.845827729757275],
    'UIO': [-78.57160966654635, -0.4180073651030667, -78.36973588724948, -0.06610523586538203],
}


# Create your models here.
class Session(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)
    city = models.CharField(max_length=20, choices=CITIES)
    active = models.BooleanField(default=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    real_users = models.SmallIntegerField()
    simulated_users = models.SmallIntegerField()
    min_lon = models.FloatField()
    min_lat = models.FloatField()
    max_lon = models.FloatField()
    max_lat = models.FloatField()
    travel_cost = models.FloatField(null=True)


class SessionUser(models.Model):
    ACTIVITIES = (
        ('amenity:post_office', 'post office'),
        ('shop:mall', 'shop mall'),
        ('amenity:restaurant', 'restaurant'),
        ('shop:supermarket', 'supermarket'),
        ('shop:convenience', 'convenience'),
        ('leisure:swimming_pool', 'swimming pool'),
        ('amenity:bar', 'bar'),
        ('amenity:fast_food', 'fast food'),
        ('amenity:cafe', 'cafe'),
        ('leisure:fitness_centre', 'fitness centre'),
        ('amenity:pub', 'pub'),
    )

    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    join_time = models.DateTimeField(auto_now_add=True)
    origin = models.BigIntegerField()
    destination = models.BigIntegerField(null=True)
    activity = models.CharField(max_length=50, choices=ACTIVITIES, null=True)
    vehicle = models.SmallIntegerField(null=True)
    ready_to_travel = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(SessionUser, self).__init__(*args, **kwargs)
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


class SessionPlan(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    activity = models.CharField(max_length=50)
    travel_cost = models.FloatField(null=True)


class SessionPlanDetail(models.Model):
    plan = models.ForeignKey(SessionPlan, on_delete=models.CASCADE)
    node_i = models.BigIntegerField()
    node_j = models.BigIntegerField()


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


class SessionActivity(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    activity = models.CharField(max_length=50)
