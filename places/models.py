from django.db import models

from allergies.models import Allergen, CommonRegion
from places.services.vegetation_collector import IVegetationCollector
from places.services.plantnet import PlantNet


class Place(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    northeast_latitude = models.FloatField()
    northeast_longitude = models.FloatField()
    southwest_latitude = models.FloatField()
    southwest_longitude = models.FloatField()
    vegetation_collector: IVegetationCollector = PlantNet()  # Dependency Injection

    def fetch_vegetation_data(self):
        return self.vegetation_collector.get_data(self)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class City(Place):
    region = models.ForeignKey(CommonRegion, on_delete=models.PROTECT, db_column='region_id')

    class Meta:
        db_table = "cities"
        db_table_comment = "Table containing coordinate information of cities of Türkiye"


class District(Place):
    city = models.ForeignKey(City, on_delete=models.PROTECT, default=None, db_column="city_id")

    def __str__(self):
        return self.name + " - " + self.city.name

    class Meta:
        db_table = "districts"
        db_table_comment = "Table containing coordinate information of districts of Türkiye"


class Vegetation(models.Model):
    gbif_number = models.IntegerField()
    last_update_date = models.DateTimeField(auto_now=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    allergen = models.ForeignKey(Allergen, on_delete=models.PROTECT, default=None, db_column="allergen_id")

    def __str__(self):
        return self.allergen.name + " - " + self.allergen.family

    class Meta:
        abstract = True


class CityVegetation(Vegetation):
    city = models.ForeignKey(City, on_delete=models.PROTECT, default=None, db_column="city_id")

    def __str__(self):
        return self.allergen.name + " - " + self.allergen.family + ": " + self.city.name

    class Meta:
        db_table = "city_vegetations"
        db_table_comment = "Table containing vegetation information of cities of Türkiye"


class DistrictVegetation(Vegetation):
    district = models.ForeignKey(District, on_delete=models.PROTECT, default=None, db_column="district_id")

    def __str__(self):
        return self.allergen.name + " - " + self.allergen.family + ": " + self.district.name

    class Meta:
        db_table = "district_vegetations"
        db_table_comment = "Table containing vegetation information of districts of Türkiye"
