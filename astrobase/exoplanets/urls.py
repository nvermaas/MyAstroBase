from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'exoplanets'

urlpatterns = [
     path('exoplanets/', views.ExoplanetsView.as_view(), name='exoplanets'),
     path('exoplanets-all/', views.ExoplanetsAllView.as_view(), name='exoplanets-all'),

     # update the exoplanets database based on the exoplanets.csv file
     path('exoplanets/update/', views.UpdateExoplanets.as_view(), name='update_exoplanets'),

]
urlpatterns = format_suffix_patterns(urlpatterns)