from django.db import models

from places.models import District
from users.models import AllergicUser


class AIModel(models.Model):
    name = models.CharField(max_length=255)
    file_path = models.FileField(upload_to="models/", blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (self.name + ": last updated at " + str(self.update_date.day) +
                "/" + str(self.update_date.month) + "/" + str(self.update_date.year))

    class Meta:
        db_table = "models"
        db_table_comment = "Table that contains AI model information for AllerGeo"


class AIAllergyAttackPrediction(models.Model):
    user = models.ForeignKey(AllergicUser, on_delete=models.PROTECT, default=None, db_column="user_id")
    date = models.DateTimeField()
    district = models.ForeignKey(District, on_delete=models.PROTECT, default=None, db_column="district_id")
    ai_prediction = models.FloatField(blank=True, null=True)
    had_allergy_attack = models.BooleanField(blank=True, null=True)
    model = models.ForeignKey(AIModel, on_delete=models.PROTECT, default=None, db_column="model_id")

    def __str__(self):
        return str(self.ai_prediction) + " - " + str(self.had_allergy_attack)

    class Meta:
        db_table = "ai_allergy_attack_predictions"
        db_table_comment = "Table that contains predictions and actual results for each district at the travel for AllerGeo"

