# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Session(models.Model):
    CITIES = (
        ('MEL', 'Melbourne'),
        ('MHK', 'Manhattan'),
        ('UIO', 'Quito'),
    )

    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)
    city = models.CharField(max_length=20, choices=CITIES)
    current = models.BooleanField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    real_users = models.SmallIntegerField()
    simulated_users = models.SmallIntegerField()


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

    session_id = models.ForeignKey(Session, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    join_time = models.DateTimeField(auto_now_add=True)
    creator = models.BooleanField()
    origin = models.BigIntegerField()
    destination = models.BigIntegerField()
    activity = models.CharField(max_length=50, choices=ACTIVITIES)
    vehicle = models.SmallIntegerField(null=True)


class SessionPlan(models.Model):
    session_id = models.ForeignKey(Session, on_delete=models.CASCADE)
    travel_cost = models.FloatField()


class SessionPlanDetail(models.Model):
    plan_id = models.ForeignKey(SessionPlan, on_delete=models.CASCADE)
    edge_i = models.BigIntegerField()
    edge_j = models.BigIntegerField()
