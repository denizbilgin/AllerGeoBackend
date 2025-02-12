from rest_framework.viewsets import ViewSet
from AllerGeoBackend.utilities import turkish_uppercase, find_similar_place
from .models import *
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
import rest_framework.status as status
from drf_yasg import openapi


class CityView(ViewSet):
    @swagger_auto_schema(responses={200: CitySerializer(many=True)})
    def list(self, request):
        cities = City.objects.all()
        serialized_cities = CitySerializer(cities, many=True)
        return Response(serialized_cities.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=CitySerializer, responses={201: CitySerializer, 400: "Invalid Data"})
    def create(self, request):
        serializer = CitySerializer(data=request.data)
        if serializer.is_valid():
            city = serializer.save()
            return Response(CitySerializer(city).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={200: CitySerializer, 404: "City not found."})
    def retrieve(self, request, pk=None):
        try:
            city = City.objects.get(pk=pk)
            serialized_city = CitySerializer(city)
            return Response(serialized_city.data, status=status.HTTP_200_OK)
        except City.DoesNotExist:
            return Response({"Error": "City not found."}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(request_body=CitySerializer, responses={200: CitySerializer, 400: "Invalid Data", 404: "City Not Found"})
    def partial_update(self, request, pk=None):
        try:
            city = City.objects.get(pk=pk)
        except City.DoesNotExist:
            return Response({"Error": "City not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CitySerializer(city, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={204: "No Content", 404: "City not found"})
    def destroy(self, request, pk=None):
        try:
            city = City.objects.get(pk=pk)
            city.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except City.DoesNotExist:
            return Response({"Error": "City not found."}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(responses={200: CitySerializer, 404: "City or Vegetation Data not found."})
    def retrieve_by_name(self, request, name=None):
        name = turkish_uppercase(name)
        try:
            name = find_similar_place(name).strip()
            city = City.objects.get(name=name)
            serialized_city = CitySerializer(city)
            return Response(serialized_city.data, status=status.HTTP_200_OK)
        except City.DoesNotExist:
            return Response({"Error": "City not found."}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(responses={200: "JSON Data", 404: "City not found."})
    def fetch_vegetation_data(self, request, pk=None):
        try:
            city = City.objects.get(pk=pk)
            vegetation_data = city.fetch_vegetation_data()

            if not vegetation_data:
                return Response({"Error": "Vegetation Data not found."}, status=status.HTTP_404_NOT_FOUND)

            serialized_vegetation_data = CityVegetationSerializer(vegetation_data, many=True)
            return Response(serialized_vegetation_data.data, status=status.HTTP_200_OK)
        except City.DoesNotExist:
            return Response({"Error": "City not found."}, status=status.HTTP_404_NOT_FOUND)


class DistrictView(ViewSet):
    @swagger_auto_schema(responses={200: DistrictSerializer(many=True)})
    def list(self, request):
        districts = District.objects.all()
        serialized_districts = DistrictSerializer(districts, many=True)
        return Response(serialized_districts.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'latitude': openapi.Schema(type=openapi.TYPE_NUMBER),
                'longitude': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_DECIMAL),
                'northeast_latitude': openapi.Schema(type=openapi.TYPE_NUMBER),
                'northeast_longitude': openapi.Schema(type=openapi.TYPE_NUMBER),
                'southwest_latitude': openapi.Schema(type=openapi.TYPE_NUMBER),
                'southwest_longitude': openapi.Schema(type=openapi.TYPE_NUMBER),
                'city_id': openapi.Schema(type=openapi.TYPE_INTEGER)
            },
            required=['name', 'latitude', 'longitude', 'northeast_latitude', 'northeast_longitude', 'southwest_latitude',
                      "southwest_longitude", "city_id"]),
        responses={201: DistrictSerializer, 400: "Invalid Data"})
    def create(self, request):
        serializer = DistrictSerializer(data=request.data)
        if serializer.is_valid():
            district = serializer.save()
            return Response(DistrictSerializer(district).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={200: DistrictSerializer, 404: "District not found."})
    def retrieve(self, request, pk=None):
        try:
            district = District.objects.get(pk=pk)
            serialized_district = DistrictSerializer(district)
            return Response(serialized_district.data, status=status.HTTP_200_OK)
        except District.DoesNotExist:
            return Response({"Error": "District not found."}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'latitude': openapi.Schema(type=openapi.TYPE_NUMBER),
                'longitude': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_DECIMAL),
                'northeast_latitude': openapi.Schema(type=openapi.TYPE_NUMBER),
                'northeast_longitude': openapi.Schema(type=openapi.TYPE_NUMBER),
                'southwest_latitude': openapi.Schema(type=openapi.TYPE_NUMBER),
                'southwest_longitude': openapi.Schema(type=openapi.TYPE_NUMBER),
                'city_id': openapi.Schema(type=openapi.TYPE_INTEGER)
            },
            required=['name', 'latitude', 'longitude', 'northeast_latitude', 'northeast_longitude', 'southwest_latitude',
                      "southwest_longitude", "city_id"]),
        responses={200: DistrictSerializer, 400: "Invalid Data", 404: "District Not Found"})
    def partial_update(self, request, pk=None):
        try:
            district = District.objects.get(pk=pk)
        except District.DoesNotExist:
            return Response({"Error": "District not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DistrictSerializer(district, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={204: "No Content", 404: "District not found"})
    def destroy(self, request, pk=None):
        try:
            district = District.objects.get(pk=pk)
            district.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except District.DoesNotExist:
            return Response({"Error": "District not found."}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(responses={200: DistrictSerializer, 404: "District or Vegetation Data not found."})
    def retrieve_by_name(self, request, name=None):
        name = turkish_uppercase(name)
        try:
            name = find_similar_place(name).strip()
            district = District.objects.get(name=name)
            serialized_district = DistrictSerializer(district)
            return Response(serialized_district.data, status=status.HTTP_200_OK)
        except District.DoesNotExist:
            return Response({"Error": "District not found."}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(responses={200: "JSON Data", 404: "City not found."})
    def fetch_vegetation_data(self, request, pk=None):
        try:
            district = District.objects.get(pk=pk)
            vegetation_data = district.fetch_vegetation_data()
            print(vegetation_data)
            if not vegetation_data:
                return Response({"Error": "Vegetation Data not found."}, status=status.HTTP_404_NOT_FOUND)

            serialized_vegetation_data = DistrictVegetationSerializer(vegetation_data, many=True)
            return Response(serialized_vegetation_data.data, status=status.HTTP_200_OK)
        except District.DoesNotExist:
            return Response({"Error": "District not found."}, status=status.HTTP_404_NOT_FOUND)
