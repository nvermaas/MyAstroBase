from django.urls import path
from . import views

app_name = 'starcharts_app'

urlpatterns = [
     path('starchart/', views.StarChart, name='starchart'),
     path('create-starchart/', views.CreateStarChart, name='create-starchart'),
]
