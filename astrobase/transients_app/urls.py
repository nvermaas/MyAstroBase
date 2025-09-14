from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'transients_app'

urlpatterns = [
     path('transients/', views.TransientView.as_view(), name='transients'),
     path('minor_planets/', views.MinorPlanetsView.as_view(), name='minor_planets'),
     path('comet/', views.CometView.as_view(), name='comet'),
     path('planet/', views.PlanetView.as_view(), name='planet'),
     path('bright_moon/', views.BrightMoonView.as_view(), name='bright_moon'),

     # get info about an asteroid by name
     path('asteroid/', views.AsteroidView.as_view(), name='asteroid'),

     # show list of asteroids in the database
     path('asteroids/', views.AsteroidsView.as_view(), name='asteroids'),
     path('asteroids-all/', views.AsteroidsAllView.as_view(), name='asteroids-all'),

     # update the astroids database based on the asteroids.txt file
     path('update_asteroids/', views.UpdateAsteroids.as_view(), name='update_asteroids'),

     # add ra,dec to all asteroids in the asteroids table for <timestamp>
     path('update_asteroids_ephemeris/', views.UpdateAsteroidsEphemeris.as_view(), name='update_asteroids'),

     path('starmap/', views.StarMap.as_view(), name='starmap-view'),
]
urlpatterns = format_suffix_patterns(urlpatterns)