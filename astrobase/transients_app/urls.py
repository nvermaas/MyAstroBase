from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'transients_app'

urlpatterns = [
     path('transients/', views.TransientView.as_view(), name='transients'),
     path('minor_planets/', views.MinorPlanetsView.as_view(), name='minor_planets'),
]
urlpatterns = format_suffix_patterns(urlpatterns)