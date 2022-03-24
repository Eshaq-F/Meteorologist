from django.contrib import admin
from meteorology.models import City, ClimaticCondition

# Register your models here.
admin.site.register(City)
admin.site.register(ClimaticCondition)