from django.urls import path

from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.views import obtain_auth_token
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [


   path('my_astrobase/obtain-auth-token/', csrf_exempt(obtain_auth_token)),
    # --- GUI ---
    # ex: /astrobase/
    path('', views.IndexView.as_view(), name='index'),

    # --- REST API ---
    # ex: /astrobase/observations/
    path('observations2/', views.Observation2ListViewAPI.as_view()),
    path('observations2/<int:pk>/', views.Observation2DetailsViewAPI.as_view(),name='observation2-detail-view-api'),
    path('projects/', views.ProjectListViewAPI.as_view()),
    path('collections2/', views.Collection2ListViewAPI.as_view()),
    path('collections2/<int:pk>/', views.Collection2DetailsViewAPI.as_view(), name='collection2-detail-view-api'),

    # ex: /astrobase/jobs/
    path('jobs/', views.JobListViewAPI.as_view()),

    # ex: /astrobase/boxes/
    path('boxes/', views.Observation2BoxesListView.as_view()),

    # ex: /astrobase/jobs/5/
    path('jobs/<int:pk>/', views.JobDetailsViewAPI.as_view(), name='job-detail-view-api'),

    path('cutout_directories/', views.CutoutDirectoryListView.as_view()),
    path('cutout_directories/<directory>/', views.CutoutDirectoryDetailsView.as_view()),

    path('cutouts/', views.CutoutListView.as_view()),
    path('cutouts/<filename>/', views.CutoutDetailsView.as_view()),

    # --- custom requests ---
    # ex: /astrobase/get_next_taskid?timestamp=2019-04-05
    path('get_next_taskid',
         views.GetNextTaskIDView.as_view(),
         name='get-next-taskid-view'),

    # ex: /astrobase/post_dataproducts&taskid=190405034
    path('post_dataproducts',
         views.PostDataproductsView.as_view(),
         name='post-dataproducts-view'),

    path('upload/', views.upload_file, name='upload-file'),

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

    path('cutout_directories/<directory>/setthumbnail/<filename>',
         views.CutoutDirectorySetThumbnail),

    path('cutout_directories/<directory>/remove', views.RemoveCutoutDirectory),
    path('cutouts/<filename>/remove', views.RemoveCutoutImage),

    path('run-command/',
         views.RunCommandView.as_view(),
         name='run-command-view'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)