from rest_framework import serializers
from .models import StarChart

class StarChartSerializer(serializers.ModelSerializer):

    class Meta:
        model = StarChart
        fields = "__all__"