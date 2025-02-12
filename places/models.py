from django.db import models
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
    species_name = models.CharField(max_length=255)
    common_name = models.CharField(max_length=255)
    family_name = models.CharField(max_length=255)
    family_link = models.TextField(blank=True, null=True)
    images = models.TextField(blank=True, null=True)
    gbif_number = models.IntegerField()
    gbif_link = models.TextField(blank=True, null=True)
    last_update_date = models.DateTimeField(auto_now=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.common_name + " - " + self.family_name

    class Meta:
        abstract = True


class CityVegetation(Vegetation):
    city = models.ForeignKey(City, on_delete=models.PROTECT, default=None, db_column="city_id")

    def __str__(self):
        return self.common_name + " - " + self.family_name + ": " + self.city.name

    class Meta:
        db_table = "city_vegetations"
        db_table_comment = "Table containing vegetation information of cities of Türkiye"


class DistrictVegetation(Vegetation):
    district = models.ForeignKey(District, on_delete=models.PROTECT, default=None, db_column="district_id")

    def __str__(self):
        return self.common_name + " - " + self.family_name + ": " + self.district.name

    class Meta:
        db_table = "district_vegetations"
        db_table_comment = "Table containing vegetation information of districts of Türkiye"
