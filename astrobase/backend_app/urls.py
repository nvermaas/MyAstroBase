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
    # ex: /astrobase/observations/
    path('observations/', views.ObservationListViewAPI.as_view()),
    path('observations2/', views.Observation2ListViewAPI.as_view()),
    path('update_observations2/', views.UpdateObservations2.as_view()),
    path('update_collections2/', views.UpdateCollections2.as_view()),

    path('observations_minimum/', views.ObservationListMinimumViewAPI.as_view()),

    # ex: /astrobase/observations/5/
    path('observations/<int:pk>/', views.ObservationDetailsViewAPI.as_view(),name='observation-detail-view-api'),
    path('observations2/<int:pk>/', views.Observation2DetailsViewAPI.as_view(), name='observation2-detail-view-api'),

    # ex: /astrobase/projects/
    path('projects/', views.ProjectListViewAPI.as_view()),

    # ex: /astrobase/collections/
    path('collections/', views.CollectionListViewAPI.as_view()),
    path('collections2/', views.Collection2ListViewAPI.as_view()),

    # ex: /astrobase/collections/5/
    path('collections/<int:pk>/', views.CollectionDetailsViewAPI.as_view(), name='collection-detail-view-api'),
    path('collections2/<int:pk>/', views.Collection2DetailsViewAPI.as_view(), name='collection2-detail-view-api'),

    # ex: /astrobase/status/
    path('status/', views.StatusListViewAPI.as_view(),name='status-list-view-api'),

    # ex: /astrobase/jobs/
    path('jobs/', views.JobListViewAPI.as_view()),

    # ex: /astrobase/boxes/
    path('boxes/', views.Observation2BoxesListView.as_view()),

    # ex: /astrobase/jobs/5/
    path('jobs/<int:pk>/', views.JobDetailsViewAPI.as_view(), name='job-detail-view-api'),

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

    path('observations/<int:pk>/setquality/<quality>/<page>',
         views.ObservationSetQuality,
         name='observation-setquality-view'),

    path('observations/<int:pk>/sethips/<hips>/<page>',
         views.ObservationSetHips,
         name='observation-sethips-view'),

    path('observations/<int:pk>/settasktype/<type>/<page>',
         views.ObservationSetTaskType,
         name='observation-settasktype-view'),

    path('run-command/',
         views.RunCommandView.as_view(),
         name='run-command-view'),
]