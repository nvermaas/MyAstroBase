from django.urls import path
from django.conf.urls import include, url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'astro'

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.

urlpatterns = [
     # path('configuration/', views.ConfigurationListViewAPI.as_view()),
     path('moonphases/', views.MoonPhasesView.as_view(), name='moonphases'),
]
urlpatterns = format_suffix_patterns(urlpatterns)