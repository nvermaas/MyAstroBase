from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'starcharts_app'

urlpatterns = [
     # REST API
     path('starcharts-api/', views.StarChartAPIView.as_view(), name='starchart-api'),

     # functions
     path('starchart/', views.StarChartView, name='starchart'),
     path('starchart/<name>', views.StarChartView, name='starchart'),

     path('create-starchart/', views.CreateStarChart, name='create-starchart'),
     path('form-starchart/', views.FormStarChart, name='form-starchart'),
     path('form-starchart/<name>', views.FormStarChart, name='form-starchart'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
