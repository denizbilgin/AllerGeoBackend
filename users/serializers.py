from rest_framework import serializers
from places.serializers import DistrictSerializer
from users.models import AllergicUser
from users.validators import *


class UserSerializer(serializers.ModelSerializer):
    residence_district = DistrictSerializer()
    username = serializers.CharField(max_length=150, min_length=3)
    first_name = serializers.CharField(max_length=150, min_length=2)
    last_name = serializers.CharField(max_length=150, min_length=2)
    email = serializers.CharField(max_length=254, min_length=3, validators=[validate_email])
    phone_number = serializers.CharField(max_length=15, validators=[validate_phone_number])

    class Meta:
        model = AllergicUser
        fields = "__all__"
