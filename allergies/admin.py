from django.contrib import admin

from allergies.models import *

admin.site.register(AllergenType)
admin.site.register(Allergen)
admin.site.register(CommonRegion)
admin.site.register(AllergenRegion)
admin.site.register(UserAllergy)
admin.site.register(AllergyAttack)
