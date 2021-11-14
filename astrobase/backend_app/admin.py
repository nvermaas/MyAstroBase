from django.contrib import admin
from .models import Observation2, Collection2, Job, AstroFile, Cutout

@admin.register(Observation2)
class Observation2Admin(admin.ModelAdmin):
    ordering = ['-date']
    search_fields = ['name']

@admin.register(Collection2)
class Collection2Admin(admin.ModelAdmin):
    filter_horizontal = ['observations']

admin.site.register(Job)
admin.site.register(AstroFile)

@admin.register(Cutout)
class CutoutAdmin(admin.ModelAdmin):
    ordering = ['field_ra']
    search_fields = ['field_name','directory']