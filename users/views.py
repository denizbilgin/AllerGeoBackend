from rest_framework.viewsets import ViewSet, ModelViewSet

from common.FundamentalPermission import FundamentalPermission
from .models import *
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
import rest_framework.status as status
from .serializers import UserSerializer, TravelSerializer, LoginSerializer, RegisterSerializer
from drf_yasg import openapi
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import Group


class UserView(ModelViewSet):
    queryset = AllergicUser.objects.all()
    serializer_class = UserSerializer

    permission_classes = [FundamentalPermission]
    permission_type = 'crud'

    @swagger_auto_schema(responses={200: UserSerializer(many=True), 403: "You do not have permission to perform this action."})
    def list(self, request):
        if request.user.is_superuser:
            allergic_user = AllergicUser.objects.select_related("residence_district").all()
            serialized_allergic_user = UserSerializer(allergic_user, many=True)
            return Response(serialized_allergic_user.data, status=status.HTTP_200_OK)
        else:
            return Response({"Error": "You do not have permission to do this action."}, status=status.HTTP_403_FORBIDDEN)

    @swagger_auto_schema(responses={200: UserSerializer(), 404: "User not found."})
    def retrieve(self, request, pk=None):
        try:
            user = AllergicUser.objects.get(pk=pk)
        except AllergicUser.DoesNotExist:
            return Response({"Error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serialized_user = UserSerializer(user)
        return Response(serialized_user.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={200: 'JWT Token', 401: 'Invalid credentials', 404: "User not found."})
    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        username: str = request.data.get("username")
        password: str = request.data.get("password")

        try:
            user = AllergicUser.objects.get(username=username)
        except AllergicUser.DoesNotExist:
            return Response({"Error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            })

        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={200: UserSerializer, 400: "Invalid Data"})
    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(user.password)
            user.save()

            users_group = Group.objects.get(name="Users")
            user.groups.add(users_group)

            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TravelView(ModelViewSet):
    queryset = Travel.objects.all()
    serializer_class = TravelSerializer

    permission_classes = [FundamentalPermission]
    permission_type = 'crud'

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

    @swagger_auto_schema(
        responses={200: TravelSerializer, 404: "User or Travel not found."})
    def retrieve_travel(self, request, pk=None, travel_id=None):
        try:
            user = AllergicUser.objects.get(pk=pk)
            travel = Travel.objects.get(user=user, id=travel_id)

            serialized_travel = TravelSerializer(travel)
            return Response(serialized_travel.data, status=status.HTTP_200_OK)
        except AllergicUser.DoesNotExist:
            return Response({"Error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Travel.DoesNotExist:
            return Response({"Error": "Travel not found."}, status=status.HTTP_404_NOT_FOUND)
