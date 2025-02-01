from django.db import models
from django.utils.timezone import now
from places.models import District
from users.models import AllergicUser, Travel
import os


class AIModel(models.Model):
    name = models.CharField(max_length=255)
    file_path = models.FileField(upload_to="models/", blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update_date = models.DateTimeField(auto_now=True)
    version = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.pk:
            self.version += 1
            self.last_update_date = now()

        if self.file_path:
            file_extension = os.path.splitext(self.file_path.name)[1]
            new_file_name = f"{self.name}-{self.version}{file_extension}"
            self.file_path.name = new_file_name

        super().save(*args, **kwargs)

    def __str__(self):
        return (self.name + ": last updated at " + str(self.last_update_date.day) +
                "/" + str(self.last_update_date.month) + "/" + str(self.last_update_date.year))

    class Meta:
        db_table = "models"
        db_table_comment = "Table that contains AI model information for AllerGeo"


class AIAllergyAttackPrediction(models.Model):
    user = models.ForeignKey(AllergicUser, on_delete=models.PROTECT, default=None, db_column="user_id")
    date = models.DateTimeField()
    district = models.ForeignKey(District, on_delete=models.PROTECT, default=None, db_column="district_id")
    ai_prediction = models.FloatField(blank=True, null=True, default=0)
    had_allergy_attack = models.BooleanField(blank=True, null=True)
    model = models.ForeignKey(AIModel, on_delete=models.PROTECT, db_column="model_id", blank=True, null=True)
    travel = models.ForeignKey(Travel, on_delete=models.PROTECT, default=None, null=True)

    def __str__(self):
        return str(self.ai_prediction) + " - " + str(self.had_allergy_attack) + ": model name is " + self.model.name

    class Meta:
        db_table = "ai_allergy_attack_predictions"
        db_table_comment = "Table that contains predictions and actual results for each district at the travel for AllerGeo"

