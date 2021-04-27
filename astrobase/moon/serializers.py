from rest_framework import serializers

# no model is used
# https://medium.com/django-rest-framework/django-rest-framework-viewset-when-you-don-t-have-a-model-335a0490ba6f
class MoonPhasesSerializer(serializers.Serializer):
    phase = serializers.CharField(max_length=15)
    date  = serializers.DateField()
    time = serializers.TimeField()

