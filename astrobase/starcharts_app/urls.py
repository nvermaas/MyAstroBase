from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'starcharts_app'

urlpatterns = [
     path('starchart/', views.StarChartView, name='starchart'),
     path('create-starchart/', views.CreateStarChart, name='create-starchart'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
