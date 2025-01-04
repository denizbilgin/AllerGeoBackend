from rest_framework import serializers
from .models import *


class AllergenTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllergenType
        fields = '__all__'


class AllergenSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255, min_length=2)
    allergen_type = AllergenTypeSerializer(read_only=True)
    allergen_type_id = serializers.IntegerField(write_only=True)

    def validate(self, attrs):
        allergen_type_id = attrs.get('allergen_type_id')

        try:
            allergen_type = AllergenType.objects.get(pk=allergen_type_id)
        except AllergenType.DoesNotExist:
            raise serializers.ValidationError("Invalid allergen type ID.")
        return attrs

    class Meta:
        model = Allergen
        fields = "__all__"


class CommonRegionSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255, min_length=2)

    class Meta:
        model = CommonRegion
        fields = "__all__"


class AllergenRegionSerializer(serializers.ModelSerializer):
    allergen = AllergenSerializer(read_only=True)
    allergen_id = serializers.IntegerField(write_only=True)

    common_region = CommonRegionSerializer(read_only=True)
    common_region_id = serializers.IntegerField(write_only=True)

    def validate(self, attrs):
        allergen_id = attrs.get('allergen_id')
        common_region_id = attrs.get('common_region_id')

        try:
            allergen = Allergen.objects.get(pk=allergen_id)
        except Allergen.DoesNotExist:
            raise serializers.ValidationError("Invalid allergen ID.")
        try:
            common_region = CommonRegion.objects.get(pk=common_region_id)
        except CommonRegion.DoesNotExist:
            raise serializers.ValidationError("Invalid common region ID.")
        return attrs

    class Meta:
        model = AllergenRegion
        fields = "__all__"
