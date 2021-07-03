from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'exoplanets'

urlpatterns = [
     path('exoplanets/', views.ExoplanetsView.as_view(), name='exoplanets'),

     # update the exoplanets database based on the exoplanets.csv file
     path('update_exoplanets/', views.UpdateExoplanets.as_view(), name='update_exoplanets'),

]
urlpatterns = format_suffix_patterns(urlpatterns)