from rest_framework import serializers
from places.models import *


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"

    def validate(self, attrs):
        if self.partial:
            return attrs

        if attrs["northeast_latitude"] <= attrs['southwest_latitude']:
            raise serializers.ValidationError({
                'northeast_latitude': 'Northeast latitude must be greater than southwest latitude.'
            })
        if attrs['northeast_longitude'] <= attrs['southwest_longitude']:
            raise serializers.ValidationError({
                'northeast_longitude': 'Northeast longitude must be greater than southwest longitude.'
            })
        return attrs


class CitySerializer(PlaceSerializer):
    class Meta(PlaceSerializer.Meta):
        model = City


class DistrictSerializer(PlaceSerializer):
    city = CitySerializer(read_only=True)
    city_id = serializers.IntegerField(write_only=True)

    def validate(self, attrs):
        city_id = attrs.get('city_id')

        try:
            city = City.objects.get(pk=city_id)
        except City.DoesNotExist:
            raise serializers.ValidationError("Invalid city ID.")
        return attrs

    class Meta(PlaceSerializer.Meta):
        model = District
        fields = "__all__"
