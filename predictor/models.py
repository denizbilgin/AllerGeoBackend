from django.db import models

from places.models import District
from users.models import AllergicUser


class AIAllergyAttackPrediction(models.Model):
    user = models.ForeignKey(AllergicUser, on_delete=models.PROTECT, default=None, db_column="user_id")
    date = models.DateTimeField()
    district = models.ForeignKey(District, on_delete=models.PROTECT, default=None, db_column="district_id")
    ai_prediction = models.FloatField()
    had_allergy_attack = models.BooleanField()

    def __str__(self):
        return str(self.ai_prediction) + " - " + str(self.had_allergy_attack)

    class Meta:
        db_table = "ai_allergy_attack_predictions"
        db_table_comment = "Table that contains predictions and actual results for each district at the travel for AllerGeo"
