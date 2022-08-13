from django import forms
from django.forms import ModelForm
from .models import StarChart

class StarChartForm(ModelForm):
      class Meta:
            model = StarChart
            fields = ['name','ra','dec','radius_ra','radius_dec','rotation','magnitude_limit',
                      'diagram_size','display_width','display_height','label_field','font_size','font_color',
                      'curve_width','curve_color','star_color','background','scheme','source',
                      'dimmest_mag','brightest_mag','min_d','max_d']
            labels = {
                'radius_ra': 'R (RA)',
                'radius_dec': 'R (dec)',
                'magnitude_limit': 'M limit',
                'dimmest_mag': 'dimmest M',
                'brightest_mag': 'brightest M',
                'display_width': 'Width',
                'display_height': 'Height',
            }

