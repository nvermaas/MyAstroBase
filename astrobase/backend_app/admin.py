from django.contrib import admin
from .models import Status, DataProduct, Observation, Collection, Command, Job

@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    ordering = ['-date']
    search_fields = ['name']

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    filter_horizontal = ['observations']

#admin.site.register(Observation)

admin.site.register(Status)
admin.site.register(DataProduct)
admin.site.register(Command)
admin.site.register(Job)
#admin.site.register(Collection)
