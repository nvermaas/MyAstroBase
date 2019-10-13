from django.contrib import admin
from .models import Status, DataProduct, Observation

admin.site.register(Status)
admin.site.register(DataProduct)
admin.site.register(Observation)