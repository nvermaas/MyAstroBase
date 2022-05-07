from django import forms
from django.forms import ModelForm
from .models import StarChart

class StarChartForm(ModelForm):
      class Meta:
            model = StarChart
            fields = ['name','ra_min','ra_min','ra_max','dec_min','dec_max','magnitude_limit']


