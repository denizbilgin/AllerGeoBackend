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
    """
    @swagger_auto_schema(responses={200: TravelSerializer(many=True), 404: "User not found."})
    def retrieve_user_travels(self, request, pk=None):
        try:
            user = AllergicUser.objects.get(pk=pk)
        except AllergicUser.DoesNotExist:
            return Response({"Error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user_travels = Travel.objects.filter(user=user)
        serialized_user_travels = TravelSerializer(user_travels, many=True)
        return Response(serialized_user_travels.data, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'start_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME,
                                       description="Date and time in ISO 8601 format (e.g., 2025-01-05T14:30:00Z)"),
                "return_date": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME,
                                       description="Date and time in ISO 8601 format (e.g., 2025-01-05T14:30:00Z)")
            }),
        responses={200: TravelSerializer, 400: "Invalid Data", 404: "User or Travel not found."})
    def partial_update(self, request, pk=None, travel_id=None):
        try:
            user = AllergicUser.objects.get(pk=pk)
            travel = Travel.objects.get(pk=travel_id, user=user)
        except AllergicUser.DoesNotExist:
            return Response({"Error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Travel.DoesNotExist:
            return Response({"Error": "Travel not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TravelSerializer(travel, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={204: "No Content", 404: "User or Travel not found"})
    def destroy(self, request, pk=None, travel_id=None):
        try:
            user = AllergicUser.objects.get(pk=pk)
            travel = Travel.objects.get(user=user, pk=travel_id)
            travel.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except AllergicUser.DoesNotExist:
            return Response({"Error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Travel.DoesNotExist:
            return Response({"Error": "Travel not found."}, status=status.HTTP_404_NOT_FOUND)

    """