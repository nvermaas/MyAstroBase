from django.contrib import admin
from .models import StarChart, Scheme, Stars

# Register your models here.
admin.site.register(Stars)
admin.site.register(Scheme)
admin.site.register(StarChart)
