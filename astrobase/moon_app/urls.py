from django.urls import path
from django.conf.urls import include, url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'moon_app'

urlpatterns = [
     path('moonphases/', views.MoonPhasesView.as_view(), name='moonphases'),
]
urlpatterns = format_suffix_patterns(urlpatterns)