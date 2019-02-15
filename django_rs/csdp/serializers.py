from rest_framework import serializers

import models


class SessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Session
        fields = ("id",
                  "active",
                  "min_lon",
                  "min_lat",
                  "max_lon",
                  "max_lat",
                  "travel_cost", )
