from rest_framework import serializers
from .models import Observation2,  Collection2, AstroFile, Job, Observation2Box
import logging

logger = logging.getLogger(__name__)

class Observation2Serializer(serializers.ModelSerializer):
    # this adds a 'generated_dataproducts' list with hyperlinks to the Observation API.
    # note that 'generated_dataproducts' is not defined in the DataProduct model,
    # but comes from the related_field in Observation.parent.

    parent = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=Observation2.objects.filter(task_type='master'),
        required=False,
        allow_null=True,
    )

    children = serializers.StringRelatedField(
        many=True,
        required=False,
        read_only=True
    )

    class Meta:
        model = Observation2
        fields = ('id','task_type', 'name', 'instrument','filter','taskID',
                  'field_name','field_ra','field_dec','field_fov','box',
                  'ra_min', 'ra_max','dec_min', 'dec_max','ra_dec_fov','date','size',
                  'derived_raw_image','derived_sky_plot_image','derived_annotated_image',
                  'derived_annotated_grid_image','derived_annotated_grid_eq_image','derived_annotated_stars_image','derived_sky_globe_image',
                  'derived_fits','derived_annotated_transient_image','derived_annotated_exoplanets_image',
                  'my_status','new_status','astrometry_url','job','url',
                  'data_location', 'quality','description',
                  'parent','derived_parent_taskid',
                  'exposure_in_seconds','iso','focal_length','stacked_images','magnitude',
                  'image_type','used_in_hips','children','extra','transient')



class Observation2LimitedSerializer(serializers.ModelSerializer):
    # used for collections
    # this adds a 'generated_dataproducts' list with hyperlinks to the Observation API.
    # note that 'generated_dataproducts' is not defined in the DataProduct model,
    # but comes from the related_field in Observation.parent.

    parent = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=Observation2.objects.filter(task_type='master'),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Observation2
        fields = ('id','name', 'instrument','filter','taskID',
                  'field_name','field_ra','field_dec','field_fov','box',
                  'ra_min', 'ra_max','dec_min', 'dec_max','ra_dec_fov','date','size',
                  'derived_raw_image','derived_sky_plot_image','derived_annotated_image',
                  'derived_annotated_grid_image','derived_annotated_grid_eq_image','derived_annotated_stars_image','derived_sky_globe_image',
                  'derived_fits','derived_annotated_transient_image','derived_annotated_exoplanets_image',
                  'my_status','new_status','job','astrometry_url','url',
                  'quality','description',
                  'parent','derived_parent_taskid',
                  'exposure_in_seconds','iso','focal_length','stacked_images','magnitude',
                  'image_type','used_in_hips')


class Collection2Serializer(serializers.ModelSerializer):
    observations = Observation2LimitedSerializer(many=True, read_only=True)

    class Meta:
        model = Collection2
        fields = ('id','date','name','collection_type','description','observations')


# Serializer for file uploads
class AstroFileSerializer(serializers.ModelSerializer):
    class Meta():
        model = AstroFile
        fields = "__all__"


class JobSerializer(serializers.ModelSerializer):
    class Meta():
        model = Job
        fields = "__all__"

class Observation2BoxSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Observation2Box
        fields = ('taskID','name','field_ra','field_dec','field_fov','field_name','box','image_type','quality','derived_fits')