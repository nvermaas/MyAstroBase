from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'starcharts_app'

urlpatterns = [
     # REST API
     path('stars-api/', views.StarsAPIView.as_view(), name='stars-api'),
     path('starcharts-api/', views.StarChartAPIView.as_view(), name='starchart-api'),

     # functions
     path('show-starchart/', views.ShowStarChartView, name='show-starchart'),
     path('show-starchart/<name>', views.ShowStarChartView, name='show-starchart'),

     path('starchart/', views.StarChartView, name='starchart'),
     path('starchart/<name>', views.StarChartView, name='starchart'),

     # shortcut to directly create a starchart with request parameters
     path('create-starchart/', views.CreateStarChart, name='create-starchart'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
