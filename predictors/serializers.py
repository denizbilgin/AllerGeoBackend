from rest_framework import serializers
from users.serializers import UserSerializer, TravelSerializer
from places.serializers import DistrictSerializer
from .models import AIAllergyAttackPrediction, AIModel
from users.models import AllergicUser, Travel
from places.models import District


class AIModelSerializer(serializers.ModelSerializer):
    version = serializers.IntegerField(read_only=True)

    class Meta:
        model = AIModel
        fields = "__all__"


class AIAllergyAttackPredictionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    district = DistrictSerializer(read_only=True)
    district_id = serializers.IntegerField(write_only=True)

    ai_prediction = serializers.IntegerField(min_value=0, default=0)

    model = AIModelSerializer(read_only=True)
    model_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    travel = TravelSerializer(read_only=True)
    travel_id = serializers.IntegerField(write_only=True, allow_null=True, required=False)

    def validate(self, attrs):
        if self.partial:
            return attrs

        user_id = attrs.get('user_id')
        district_id = attrs.get("district_id")
        travel_id = attrs.get("travel_id")
        model_id = attrs.get("model_id")
        selected_date = attrs.get("date")
        try:
            user = AllergicUser.objects.get(pk=user_id)
            district = District.objects.get(pk=district_id)
            if travel_id:
                travel = Travel.objects.get(pk=travel_id)
            if model_id:
                model = AIModel.objects.get(pk=model_id)
        except AllergicUser.DoesNotExist:
            raise serializers.ValidationError("Invalid User ID.")
        except District.DoesNotExist:
            raise serializers.ValidationError("Invalid District ID.")
        except Travel.DoesNotExist:
            raise serializers.ValidationError("Invalid Travel ID.")
        except AIModel.DoesNotExist:
            raise serializers.ValidationError("Invalid AI Model ID.")

        if selected_date and travel_id:
            if not (travel.start_date <= selected_date):
                raise serializers.ValidationError(
                    {"date": "The selected date must be between the travel start and return date."}
                )

        return attrs

    class Meta:
        model = AIAllergyAttackPrediction
        fields = "__all__"
