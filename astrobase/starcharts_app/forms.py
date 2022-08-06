from django import forms
from django.forms import ModelForm
from .models import StarChart

class StarChartForm(ModelForm):
      class Meta:
            model = StarChart
            fields = ['name','ra','dec','radius_ra','radius_dec','magnitude_limit',
                      'diagram_size','display_width','display_height','label_field','font_size','font_color',
                      'curve_width','curve_color','star_color','background','scheme','source',
                      'dimmest_mag','brightest_mag','min_d','max_d']


