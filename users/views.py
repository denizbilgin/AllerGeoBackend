from rest_framework.viewsets import ViewSet
from .models import *
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
import rest_framework.status as status
from .serializers import UserSerializer, TravelSerializer
from drf_yasg import openapi


class UserView(ViewSet):
    @swagger_auto_schema(responses={200: UserSerializer(many=True)})
    def list(self, request):
        allergic_user = AllergicUser.objects.select_related("residence_district").all()
        serialized_allergic_user = UserSerializer(allergic_user, many=True)
        return Response(serialized_allergic_user.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: UserSerializer(), 404: "User not found."})
    def retrieve(self, request, pk=None):
        try:
            user = AllergicUser.objects.get(pk=pk)
        except AllergicUser.DoesNotExist:
            return Response({"Error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serialized_user = UserSerializer(user)
        return Response(serialized_user.data, status=status.HTTP_200_OK)


class TravelView(ViewSet):
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
            },
            required=['start_date', "return_date"]),
        responses={201: TravelSerializer, 400: "Invalid Data"})
    def create(self, request, pk=None):
        request.data["user"] = pk
        serializer = TravelSerializer(data=request.data)
        if serializer.is_valid():
            user_travels = serializer.save()
            return Response(TravelSerializer(user_travels).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
