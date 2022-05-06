from django import forms
from django.forms import ModelForm
from .models import StarChart

class StarChartForm(ModelForm):
      class Meta:
            model = StarChart
            fields = ['name','ra_min','ra_min','ra_max','dec_min','dec_max','magnitude_limit']

class StarChartForm_xxx(forms.Form):
      name = forms.CharField(label='Name', max_length=20)
      ra_min = forms.FloatField(label='RA (min)')
      #ra_max= forms.FloatField(label='RA (max)', widget=forms.FloatField())
      #dec_min = forms.FloatField(label='dec (min)', widget=forms.FloatField())
      #dec_max= forms.FloatField(label='dec (max)', widget=forms.FloatField())
      #mag= forms.FloatField(label='Mag (max)', widget=forms.FloatField())
