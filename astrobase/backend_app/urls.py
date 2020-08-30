from django.urls import path
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [

    url(r'^my_astrobase/obtain-auth-token/$', csrf_exempt(obtain_auth_token)),

    # --- GUI ---
    # ex: /astrobase/
    path('', views.IndexView.as_view(), name='index'),

    # ex: /astrobase/task/180223003/
    path('task/<taskID>/', views.DataProductsListView.as_view(), name='dataproducts-list-view'),

    # --- REST API ---
    # ex: /astrobase/dataproducts/
    path('dataproducts/', views.DataProductListViewAPI.as_view()),

    # ex: /astrobase/dataproducts/5/
    path('dataproducts/<int:pk>/', views.DataProductDetailsViewAPI.as_view(),name='dataproduct-detail-view-api'),

    # ex: /astrobase/observations/
    path('tasks/', views.ObservationListViewAPI.as_view()),

    # ex: /astrobase/observations/
    path('observations/', views.ObservationListViewAPI.as_view()),

    # ex: /astrobase/observations/5/
    path('observations/<int:pk>/', views.ObservationDetailsViewAPI.as_view(),name='observation-detail-view-api'),

    # ex: /astrobase/projects/
    path('projects/', views.ProjectListViewAPI.as_view()),

    # ex: /astrobase/status/
    path('status/', views.StatusListViewAPI.as_view(),name='status-list-view-api'),

    # --- custom requests ---
    # ex: /astrobase/get_next_taskid?timestamp=2019-04-05
    path('get_next_taskid',
         views.GetNextTaskIDView.as_view(),
         name='get-next-taskid-view'),

    # ex: /astrobase/post_dataproducts&taskid=190405034
    path('post_dataproducts',
         views.PostDataproductsView.as_view(),
         name='post-dataproducts-view'),

    path('upload_file/',
         views.UploadFileView.as_view(),
         name='upload-file'),

    path('uploads/', views.UploadsView.as_view()),
    path('uploads/<int:pk>/', views.UploadsDetailsView.as_view()),

    # --- Commands ---
    path('observations/<int:pk>/setstatus/<new_status>/<page>',
         views.ObservationSetStatus,
         name='observation-setstatus-view'),

    path('observations/<int:pk>/setstatus_dps/<new_dps_status>/<new_obs_status>/<page>',
         views.ObservationSetStatusDataProducts,
         name='observation-dps-setstatus-view'),

    path('dataproducts/<int:pk>/setstatus/<new_status>',
         views.DataProductSetStatusView,
         name='dataproduct-setstatus-view'),

    path('observations/<int:pk>/setquality/<quality>/<page>',
         views.ObservationSetQuality,
         name='observation-setquality-view'),

    path('observations/<int:pk>/setmode/<mode>/<page>',
         views.ObservationSetMode,
         name='observation-setmode-view'),

    path('observations/<int:pk>/settasktype/<type>/<page>',
         views.ObservationSetTaskType,
         name='observation-settasktype-view'),
]