from django.contrib import admin

from places.models import *

admin.site.register(City)
admin.site.register(District)
admin.site.register(CityVegetation)
admin.site.register(DistrictVegetation)
