from rest_framework.viewsets import ViewSet
from .models import *
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
import rest_framework.status as status
from rest_framework import mixins
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg import openapi
from predictors.serializers import *


class AIModelView(ViewSet, mixins.CreateModelMixin):
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(responses={200: AIModelSerializer(many=True)})
    def list(self, request):
        ai_model = AIModel.objects.all()
        serialized_ai_model = AIModelSerializer(ai_model, many=True)
        return Response(serialized_ai_model.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "name",
                openapi.IN_FORM,
                description="Model name",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                "file_path",
                openapi.IN_FORM,
                description="File upload",
                type=openapi.TYPE_FILE,
                required=True
            ),
            openapi.Parameter(
                "description",
                openapi.IN_FORM,
                description="Optional description",
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={201: AIModelSerializer, 400: "Invalid Data"}
    )
    def create(self, request):
        serializer = AIModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "name",
                openapi.IN_FORM,
                description="Model name",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                "file_path",
                openapi.IN_FORM,
                description="File upload",
                type=openapi.TYPE_FILE,
                required=False
            ),
            openapi.Parameter(
                "description",
                openapi.IN_FORM,
                description="Optional description",
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={200: AIModelSerializer, 400: "Invalid Data", 404: "AI Model not found."}
    )
    def partial_update(self, request, pk=None):
        try:
            ai_model = AIModel.objects.get(pk=pk)
        except AIModel.DoesNotExist:
            return Response({"Error": "AI Model not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AIModelSerializer(ai_model, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={200: AIModelSerializer, 404: "AI Model not found."})
    def retrieve(self, request, pk=None):
        try:
            ai_model = AIModel.objects.get(pk=pk)
            serialized_ai_model = AIModelSerializer(ai_model)
            return Response(serialized_ai_model.data, status=status.HTTP_200_OK)
        except AIModel.DoesNotExist:
            return Response({"Error": "AI Model not found."}, status=status.HTTP_404_NOT_FOUND)


class AIAllergyAttackPredictionView(ViewSet):
    @swagger_auto_schema(responses={200: AIAllergyAttackPredictionSerializer(many=True)})
    def list(self, request):
        ai_allergy_attack_predictions = AIAllergyAttackPrediction.objects.all()
        serialized_ai_allergy_attack_predictions = AIAllergyAttackPredictionSerializer(ai_allergy_attack_predictions, many=True)
        return Response(serialized_ai_allergy_attack_predictions.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                "date": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME,
                                       description="Date and time in ISO 8601 format (e.g., 2025-01-05T14:30:00Z)"),
                "district_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "ai_prediction": openapi.Schema(type=openapi.TYPE_INTEGER),
                "had_allergy_attack": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                "model_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "travel_id": openapi.Schema(type=openapi.TYPE_INTEGER)
            },
            required=['user_id', "date", "district_id"]),
        responses={201: AIAllergyAttackPredictionSerializer, 400: "Invalid Data"})
    def create(self, request):
        serializer = AIAllergyAttackPredictionSerializer(data=request.data)
        if serializer.is_valid():
            ai_allergy_attack_prediction = serializer.save()
            return Response(AIAllergyAttackPredictionSerializer(ai_allergy_attack_prediction).data,
                            status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                "date": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME,
                                       description="Date and time in ISO 8601 format (e.g., 2025-01-05T14:30:00Z)"),
                "district_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "ai_prediction": openapi.Schema(type=openapi.TYPE_INTEGER),
                "had_allergy_attack": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                "model_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "travel_id": openapi.Schema(type=openapi.TYPE_INTEGER)
            }),
        responses={200: TravelSerializer, 400: "Invalid Data", 404: "AI Allergy Attack Prediction not found."})
    def partial_update(self, request, pk=None):
        try:
            ai_allergy_attack_prediction = AIAllergyAttackPrediction.objects.get(pk=pk)
        except AIAllergyAttackPrediction.DoesNotExist:
            return Response({"Error": "AI Allergy Attack Prediction not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AIAllergyAttackPredictionSerializer(ai_allergy_attack_prediction, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={204: "No Content", 404: "AI Allergy Attack Prediction not found"})
    def destroy(self, request, pk=None):
        try:
            ai_allergy_attack_prediction = AIAllergyAttackPrediction.objects.get(pk=pk)
            ai_allergy_attack_prediction.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except AIAllergyAttackPrediction.DoesNotExist:
            return Response({"Error": "AI Allergy Attack Prediction not found."}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(responses={200: AIAllergyAttackPredictionSerializer, 404: "AI Allergy Attack Prediction not found."})
    def retrieve(self, request, pk=None):
        try:
            ai_allergy_attack_prediction = AIAllergyAttackPrediction.objects.get(pk=pk)
            serialized_ai_allergy_attack_prediction = AIAllergyAttackPredictionSerializer(ai_allergy_attack_prediction)
            return Response(serialized_ai_allergy_attack_prediction.data, status=status.HTTP_200_OK)
        except AIAllergyAttackPrediction.DoesNotExist:
            return Response({"Error": "AI Allergy Attack Prediction not found."}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(responses={200: AIAllergyAttackPredictionSerializer, 404: "User, Travel or Waypoint not found."})
    def retrieve_user_travel_waypoints(self, request, pk=None, travel_id=None):
        try:
            user = AllergicUser.objects.get(pk=pk)
            travel = Travel.objects.get(user=user, id=travel_id)

            waypoints = AIAllergyAttackPrediction.objects.filter(travel=travel, user=user)
            serialized_waypoints = AIAllergyAttackPredictionSerializer(waypoints, many=True)
            return Response(serialized_waypoints.data, status=status.HTTP_200_OK)
        except AllergicUser.DoesNotExist:
            return Response({"Error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Travel.DoesNotExist:
            return Response({"Error": "Travel not found."}, status=status.HTTP_404_NOT_FOUND)
        except AIAllergyAttackPrediction.DoesNotExist:
            return Response({"Error": "Waypoint not found."}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "date": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME,
                                           description="Date and time in ISO 8601 format (e.g., 2025-01-05T14:30:00Z)"),
                    "district_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                },
                required=["date", "district_id"]
            )
        ),
        responses={201: AIAllergyAttackPredictionSerializer(many=True), 400: "Invalid Data"},
    )
    def create_travel_waypoints(self, request, pk=None, travel_id=None):
        try:
            user = AllergicUser.objects.get(pk=pk)
            travel = Travel.objects.get(user=user, id=travel_id)
        except AllergicUser.DoesNotExist:
            return Response({"Error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Travel.DoesNotExist:
            return Response({"Error": "Travel not found."}, status=status.HTTP_404_NOT_FOUND)

        if not isinstance(request.data, list):
            return Response({"Error": "Data should be a list of objects."}, status=status.HTTP_400_BAD_REQUEST)

        created_waypoints = []
        for waypoint in request.data:
            waypoint["user_id"] = user.id
            waypoint["travel_id"] = travel.id

            serializer = AIAllergyAttackPredictionSerializer(data=waypoint)
            if serializer.is_valid():
                created_waypoints.append(serializer.save())
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        created_waypoints = sorted(created_waypoints, key=lambda x: x.date)
        return Response(AIAllergyAttackPredictionSerializer(created_waypoints, many=True).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        responses={200: AIAllergyAttackPredictionSerializer, 404: "User, Travel ol Waypoint not found."})
    def retrieve_waypoint(self, request, pk=None, travel_id=None, waypoint_id=None):
        try:
            user = AllergicUser.objects.get(pk=pk)
            travel = Travel.objects.get(id=travel_id, user=user)
            waypoint = AIAllergyAttackPrediction.objects.get(id=waypoint_id, travel=travel)
        except AllergicUser.DoesNotExist:
            return Response({"Error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Travel.DoesNotExist:
            return Response({"Error": "Travel not found."}, status=status.HTTP_404_NOT_FOUND)
        except AIAllergyAttackPrediction.DoesNotExist:
            return Response({"Error": "Waypoint not found."}, status=status.HTTP_404_NOT_FOUND)

        serialized_waypoint = AIAllergyAttackPredictionSerializer(waypoint)
        return Response(serialized_waypoint.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "date": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME,
                                       description="Date and time in ISO 8601 format (e.g., 2025-01-05T14:30:00Z)"),
                "district_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "ai_prediction": openapi.Schema(type=openapi.TYPE_INTEGER),
                "had_allergy_attack": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                "model_id": openapi.Schema(type=openapi.TYPE_INTEGER),
            }),
        responses={200: AIAllergyAttackPredictionSerializer, 400: "Invalid Data", 404: "User, Travel or Waypoint not found."})
    def partial_update_waypoint(self, request, pk=None, travel_id=None, waypoint_id=None):
        try:
            user = AllergicUser.objects.get(pk=pk)
            travel = Travel.objects.get(id=travel_id, user=user)
            waypoint = AIAllergyAttackPrediction.objects.get(id=waypoint_id, travel=travel)
        except AllergicUser.DoesNotExist:
            return Response({"Error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Travel.DoesNotExist:
            return Response({"Error": "Travel not found."}, status=status.HTTP_404_NOT_FOUND)
        except AIAllergyAttackPrediction.DoesNotExist:
            return Response({"Error": "Waypoint not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AIAllergyAttackPredictionSerializer(waypoint, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={204: "No Content", 404: "User, Travel or Waypoint not found"})
    def destroy_waypoint(self, request, pk=None, travel_id=None, waypoint_id=None):
        try:
            user = AllergicUser.objects.get(pk=pk)
            travel = Travel.objects.get(id=travel_id, user=user)
            waypoint = AIAllergyAttackPrediction.objects.get(id=waypoint_id, travel=travel)
        except AllergicUser.DoesNotExist:
            return Response({"Error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Travel.DoesNotExist:
            return Response({"Error": "Travel not found."}, status=status.HTTP_404_NOT_FOUND)
        except AIAllergyAttackPrediction.DoesNotExist:
            return Response({"Error": "Waypoint not found."}, status=status.HTTP_404_NOT_FOUND)

        waypoint.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
