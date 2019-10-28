from rest_framework import serializers
from .models import DataProduct, Observation, Status, AstroFile
import logging

logger = logging.getLogger(__name__)

class StatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Status
        fields = ('id','name','timestamp','property_taskID','property_task_type')


class DataProductSerializer(serializers.ModelSerializer):
    # this adds a 'parent_observation' list with hyperlinks to the DataProduct API.
    # note that 'generatedByObservation' is not defined in the DataProduct model, but in the Observation model.

    parent = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=Observation.objects.all(),
        required=False,
    )

    status_history = serializers.StringRelatedField(
        many=True,
        required=False,
    )

    class Meta:
        model = DataProduct
        fields = ('id','task_type','dataproduct_type','filename','description',
                  'taskID','creationTime','size','quality',
                  'my_status','new_status','status_history','parent','property_url')


class ObservationSerializer(serializers.ModelSerializer):
    # this adds a 'generated_dataproducts' list with hyperlinks to the Observation API.
    # note that 'generated_dataproducts' is not defined in the DataProduct model,
    # but comes from the related_field in Observation.parent.

    generated_dataproducts = serializers.StringRelatedField(
        many=True,
        required=False,
    )

    status_history = serializers.StringRelatedField(
        many=True,
        required=False,
    )

    class Meta:
        model = Observation
        fields = ('id','task_type', 'name', 'observing_mode','process_type','taskID',
                  'field_name','field_ra','field_dec','field_fov',
                  'creationTime','date','size',
                  'derived_raw_image','derived_sky_plot_image','derived_annotated_image',
                  'my_status','new_status','status_history','job',
                  'generated_dataproducts','data_location', 'quality','description')

# Serializer for file uploads
class AstroFileSerializer(serializers.ModelSerializer):
    class Meta():
        model = AstroFile
        fields = "__all__"
