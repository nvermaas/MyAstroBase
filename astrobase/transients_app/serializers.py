from rest_framework import serializers

# no model is used
# https://medium.com/django-rest-framework/django-rest-framework-viewset-when-you-don-t-have-a-model-335a0490ba6f
class TransientSerializer(serializers.Serializer):
    number = serializers.IntegerField()
    name = serializers.CharField(max_length=15)
    period = serializers.CharField(max_length=15)
    absolute_magnitude  = serializers.DateField()
    updated_at = serializers.TimeField()


class MinorPlanetSerializer(serializers.Serializer):
    number = serializers.IntegerField()
    name = serializers.CharField(max_length=15)
    period = serializers.CharField(max_length=15)
    absolute_magnitude  = serializers.DateField()
    updated_at = serializers.TimeField()