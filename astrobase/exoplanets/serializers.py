from rest_framework import serializers
from .models import Exoplanet

class ExoplanetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Exoplanet
        fields = "__all__"