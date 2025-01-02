from rest_framework import serializers


def validate_email(value):
    if "@" not in value or "." not in value:
        raise serializers.ValidationError("Please enter a valid email.")
    return value


def validate_phone_number(value):
    if not value.isdigit():
        raise serializers.ValidationError("Phone number must only contain digits.")
    if len(value) < 10 or len(value) > 13:
        raise serializers.ValidationError("Please enter a valid phone number")
    return value
