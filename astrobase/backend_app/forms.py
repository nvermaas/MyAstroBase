from django import forms
STATUS_CHOICES = [('defined','defined'),
                  ('scheduled','scheduled'),
                  ('running','running'),
                  ('removed','removed'),
                  ('error','error')
                ]

class FilterForm(forms.Form):
     status = forms.MultipleChoiceField(required=True, widget=forms.CheckboxSelectMultiple, choices=STATUS_CHOICES)
