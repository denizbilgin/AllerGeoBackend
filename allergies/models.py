from django.db import models

from places.models import District
from users.models import AllergicUser


class AllergenType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "allergen_types"
        db_table_comment = "Table that contains allergen categories for AllerGeo"


class Allergen(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    allergen_type = models.ForeignKey(AllergenType, on_delete=models.PROTECT, default=None, db_column="allergen_type_id")

    def __str__(self):
        return self.name + " - " + self.allergen_type.name

    class Meta:
        db_table = "allergens"
        db_table_comment = "A table that contains common allergies for AllerGeo"


class CommonRegion(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "common_regions"
        db_table_comment = "Table that contains regions of Türkiye for AllerGeo"


class AllergenRegion(models.Model):
    allergen = models.ForeignKey(Allergen, on_delete=models.PROTECT, default=None, db_column="allergen_id")
    common_region = models.ForeignKey(CommonRegion, on_delete=models.PROTECT, default=None, db_column="common_region_id")

    def __str__(self):
        return self.allergen.name + " - " + self.common_region.name

    class Meta:
        db_table = "allergen_regions"
        db_table_comment = "Table that contains allergen regions for AllerGeo"


class UserAllergy(models.Model):
    user = models.ForeignKey(AllergicUser, on_delete=models.PROTECT, default=None, db_column="user_id")
    allergen = models.ForeignKey(Allergen, on_delete=models.PROTECT, default=None, db_column="allergen_id")
    creation_date = models.DateTimeField(auto_now_add=True)
    importance_level = models.IntegerField(default=1)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name + " - " + self.allergen.name

    class Meta:
        db_table = "user_allergies"
        db_table_comment = "Table that contains allergy data of users for AllerGeo"


class AllergyAttack(models.Model):
    user = models.ForeignKey(AllergicUser, on_delete=models.PROTECT, default=None, db_column="user_id")
    district = models.ForeignKey(District, on_delete=models.PROTECT, default=None, db_column="district_id")
    date = models.DateTimeField()
    allergen = models.ForeignKey(Allergen, on_delete=models.PROTECT, default=None, db_column="allergen_id")
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return (self.user.first_name + " " + self.user.last_name + " - " + self.allergen.name +
                " : " + str(self.date.day) + "/" + str(self.date.month) + "/" + str(self.date.year))

    class Meta:
        db_table = "allergy_attacks"
        db_table_comment = "Table that contains allergy attack information of users for AllerGeo"


# TODO: validatorsları silip bir validate dosyasına topla
# TODO: Viewlerde bug ara
# TODO: userin aynı alerjeni bir kere içermesi gibi ve buna benzer durumları kontrol et
# TODO: items adlandırmasını değiştir
# TODO: status kodları kontrol et
# TODO: partialleri kontrol et
