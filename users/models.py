from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date
from places.models import District
from django.contrib.postgres.fields import ArrayField


class MembershipType(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField()

    def __str__(self):
        return self.name + " membership - " + str(self.price) + " TL"

    class Meta:
        db_table = "membership_types"
        db_table_comment = "Table that contains membership types of users for AllerGeo"


class AllergicUser(AbstractUser):
    photo = models.ImageField(upload_to="profile_photos/", blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    residence_district = models.ForeignKey(District, on_delete=models.PROTECT, default=None,
                                           db_column="residence_district_id")
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=15)

    @property
    def age(self):
        today = date.today()
        age = today.year - self.date_of_birth.year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
        return age

    def __str__(self):
        return str(self.id) + " - " + self.first_name + " " + self.last_name

    class Meta:
        db_table = "users"
        db_table_comment = "Table that contains user information for AllerGeo"


class Membership(models.Model):
    user = models.ForeignKey(AllergicUser, on_delete=models.PROTECT, default=None, db_column="user_id")
    membership_type = models.ForeignKey(MembershipType, on_delete=models.PROTECT, default=1, db_column="membership_type_id")
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name + ": " + self.membership_type.name + ". " + str(self.start_date) + " -> " + str(self.end_date)

    class Meta:
        db_table = "memberships"
        db_table_comment = "Table that contains membership information of users for AllerGeo"


class Travel(models.Model):
    user = models.ForeignKey(AllergicUser, on_delete=models.PROTECT, default=None, db_column="user_id")
    path = ArrayField(models.IntegerField(), blank=True, default=list)
    creation_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField()
    return_date = models.DateTimeField()

    def __str__(self):
        return (self.user.first_name + " " + self.user.last_name + " - " +
                str(self.start_date.day) + "/" + str(self.start_date.month) + "/" + str(self.start_date.year))

    class Meta:
        db_table = "travels"
        db_table_comment = "Table that contains travel information of users for AllerGeo"
