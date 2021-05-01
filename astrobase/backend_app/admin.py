from django.contrib import admin
from .models import Status, DataProduct, Observation, Collection, Job

@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    ordering = ['-date']
    search_fields = ['name']

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    filter_horizontal = ['observations']

admin.site.register(Status)
#admin.site.register(DataProduct)
@admin.register(DataProduct)
class DataProductAdmin(admin.ModelAdmin):
    search_fields = ['filename']
admin.site.register(Job)

