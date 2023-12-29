from django import forms
from .models import AstroFile

STATUS_CHOICES = [('defined','defined'),
                  ('scheduled','scheduled'),
                  ('running','running'),
                  ('removed','removed'),
                  ('error','error')
                ]

class FilterForm(forms.Form):
     status = forms.MultipleChoiceField(required=True, widget=forms.CheckboxSelectMultiple, choices=STATUS_CHOICES)

class AstroFileForm(forms.ModelForm):
    class Meta:
        model = AstroFile
        fields = ['file']