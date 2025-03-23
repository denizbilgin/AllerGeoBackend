from rest_framework import serializers

from places.models import District
from places.serializers import DistrictSerializer
from users.models import AllergicUser, Travel


class UserSerializer(serializers.ModelSerializer):
    residence_district = DistrictSerializer(read_only=True)
    residence_district_id = serializers.IntegerField(write_only=True)

    username = serializers.CharField(max_length=150, min_length=3)
    first_name = serializers.CharField(max_length=150, min_length=2)
    last_name = serializers.CharField(max_length=150, min_length=2)
    email = serializers.CharField(max_length=254, min_length=3)
    phone_number = serializers.CharField(max_length=15)
    is_male = serializers.BooleanField()

    age = serializers.SerializerMethodField(read_only=True)

    def get_age(self, obj):
        return obj.age

    def validate(self, attrs):
        if self.partial:
            return attrs

        email = attrs.get('email')
        if "@" not in email or "." not in email:
            raise serializers.ValidationError("Please enter a valid email.")

        phone_number = attrs.get("phone_number")
        if not phone_number.isdigit():
            raise serializers.ValidationError("Phone number must only contain digits.")
        if len(phone_number) < 10 or len(phone_number) > 13:
            raise serializers.ValidationError("Please enter a valid phone number")

        return attrs

    class Meta:
        model = AllergicUser
        fields = "__all__"


class UserUpdateSerializer(serializers.ModelSerializer):
    residence_district = serializers.PrimaryKeyRelatedField(queryset=District.objects.all())
    date_of_birth = serializers.DateField(format="%Y-%m-%d")

    class Meta:
        model = AllergicUser
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'date_of_birth',
            'residence_district'
        ]

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        instance.residence_district = validated_data.get('residence_district', instance.residence_district)

        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class RegisterSerializer(serializers.ModelSerializer):
    residence_district_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = AllergicUser
        fields = ["username", "first_name", "last_name", "date_of_birth", "phone_number", "residence_district_id", "password", "is_male", "email"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

        def create(self, validated_data):
            user = AllergicUser.objects.create_user(**validated_data)
            return user


class TravelSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Travel
        fields = "__all__"

    def validate(self, attrs):
        if self.partial:
            return attrs

        start_date = attrs.get("start_date")
        return_date = attrs.get("return_date")

        if return_date and start_date and return_date < start_date:
            raise serializers.ValidationError("Return date cannot be earlier than start date.")

        return attrs