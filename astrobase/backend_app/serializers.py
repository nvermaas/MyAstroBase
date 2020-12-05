from rest_framework import serializers
from .models import DataProduct, Observation, Collection, Status, AstroFile, Job
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

    parent = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=Observation.objects.filter(task_type='master'),
        required=False,
        allow_null=True,
    )

    children = serializers.StringRelatedField(
        many=True,
        required=False,
        read_only=True
    )

    class Meta:
        model = Observation
        fields = ('id','task_type', 'name', 'instrument','filter','process_type','taskID',
                  'field_name','field_ra','field_dec','field_fov',
                  'ra_min', 'ra_max','dec_min', 'dec_max','ra_dec_fov','date','size',
                  'derived_raw_image','derived_sky_plot_image','derived_annotated_image',
                  'derived_annotated_grid_image','derived_annotated_stars_image','derived_sky_globe_image',
                  'derived_fits',
                  'my_status','new_status','status_history','job','astrometry_url','url',
                  'generated_dataproducts','data_location', 'quality','description',
                  'parent','derived_parent_taskid',
                  'exposure_in_seconds','iso','focal_length','stacked_images','magnitude',
                  'image_type','children')



class ObservationFullSerializer(serializers.ModelSerializer):
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

    parent = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=Observation.objects.filter(task_type='master'),
        required=False,
        allow_null=True,
    )

    children = serializers.StringRelatedField(
        many=True,
        required=False,
        read_only=True
    )

    class Meta:
        model = Observation
        fields = ('id','task_type', 'name', 'instrument','filter','process_type','taskID',
                  'field_name','field_ra','field_dec','field_fov',
                  'ra_min', 'ra_max','dec_min', 'dec_max','ra_dec_fov','date','size',
                  'derived_raw_image','derived_sky_plot_image','derived_annotated_image',
                  'derived_annotated_grid_image','derived_annotated_stars_image','derived_sky_globe_image',
                  'derived_fits',
                  'my_status','new_status','status_history','job','astrometry_url','url',
                  'generated_dataproducts','data_location', 'quality','description',
                  'parent','derived_parent_taskid',
                  'exposure_in_seconds','iso','focal_length','stacked_images','magnitude',
                  'image_type','children')


class ObservationCollectionSerializer(serializers.ModelSerializer):
    # this adds a 'generated_dataproducts' list with hyperlinks to the Observation API.
    # note that 'generated_dataproducts' is not defined in the DataProduct model,
    # but comes from the related_field in Observation.parent.

    parent = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=Observation.objects.filter(task_type='master'),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Observation
        fields = ('id','name', 'instrument','filter','taskID',
                  'field_name','field_ra','field_dec','field_fov',
                  'ra_min', 'ra_max','dec_min', 'dec_max','ra_dec_fov','date','size',
                  'derived_raw_image','derived_sky_plot_image','derived_annotated_image',
                  'derived_annotated_grid_image','derived_annotated_stars_image','derived_sky_globe_image',
                  'derived_fits',
                  'my_status','new_status','job','astrometry_url','url',
                  'quality','description',
                  'parent','derived_parent_taskid',
                  'exposure_in_seconds','iso','focal_length','stacked_images','magnitude',
                  'image_type')


class CollectionSerializer(serializers.ModelSerializer):
    observations = ObservationCollectionSerializer(many=True, read_only=True)

    class Meta:
        model = Collection
        fields = ('id','date','name','collection_type','description','observations')
        # fields = "__all__"
        # this expands the observations to more than just the id.
        #depth=1

# Serializer for file uploads
class AstroFileSerializer(serializers.ModelSerializer):
    class Meta():
        model = AstroFile
        fields = "__all__"


class JobSerializer(serializers.ModelSerializer):
    class Meta():
        model = Job
        fields = "__all__"