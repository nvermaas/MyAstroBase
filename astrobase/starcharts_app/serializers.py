from rest_framework import serializers
from .models import StarChart, Stars

class StarsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Stars
        fields = "__all__"

class StarChartSerializer(serializers.ModelSerializer):

    class Meta:
        model = StarChart
        fields = "__all__"