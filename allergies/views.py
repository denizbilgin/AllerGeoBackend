from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.decorators import action
from common.FundamentalPermission import FundamentalPermission
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
import rest_framework.status as status
from drf_yasg import openapi
from common.utilities import turkish_capitalize
from users.models import AllergicUser


class AllergenTypeView(ModelViewSet):
    queryset = AllergenType.objects.all()
    serializer_class = AllergenTypeSerializer

    permission_classes = [FundamentalPermission]
    permission_type = 'view'

    @swagger_auto_schema(responses={200: AllergenSerializer(many=True), 404: "Allergen Type not found."})
    def retrieve_allergens_by_type(self, request, pk=None):
        try:
            allergen_type = AllergenType.objects.get(pk=pk)
        except AllergenType.DoesNotExist:
            return Response({"error": "Allergen Type not found."}, status=status.HTTP_404_NOT_FOUND)

        filtered_allergens = Allergen.objects.filter(allergen_type=allergen_type)
        serialized_filtered_allergens = AllergenSerializer(filtered_allergens, many=True)
        return Response(serialized_filtered_allergens.data, status=status.HTTP_200_OK)


class AllergenView(ModelViewSet):
    queryset = Allergen.objects.all()
    serializer_class = AllergenSerializer

    permission_classes = [FundamentalPermission]
    permission_type = 'view'

    @swagger_auto_schema(responses={200: AllergenSerializer(many=True)})
    def list(self, request):
        allergens = Allergen.objects.all()
        serialized_allergens = AllergenSerializer(allergens, many=True)
        return Response(serialized_allergens.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'allergen_type_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'description': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['name', 'allergen_type_id', 'description']),
        responses={201: AllergenSerializer, 400: "Invalid Data"})
    def create(self, request):
        serializer = AllergenSerializer(data=request.data)
        if serializer.is_valid():
            allergen = serializer.save()
            return Response(AllergenSerializer(allergen).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={200: AllergenSerializer, 404: "Allergen not found."})
    def retrieve(self, request, pk=None):
        try:
            allergen = Allergen.objects.get(pk=pk)
            serialized_allergen = AllergenSerializer(allergen)
            return Response(serialized_allergen.data, status=status.HTTP_200_OK)
        except Allergen.DoesNotExist:
            return Response({"Error": "Allergen not found."}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'allergen_type_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'description': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['name', 'allergen_type_id', 'description']),
        responses={200: AllergenSerializer, 400: "Invalid Data", 404: "Allergen not found"})
    def partial_update(self, request, pk=None):
        try:
            allergen = Allergen.objects.get(pk=pk)
        except Allergen.DoesNotExist:
            return Response({"Error": "Allergen not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AllergenSerializer(allergen, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={204: "No Content", 404: "Allergen not found"})
    def destroy(self, request, pk=None):
        try:
            allergen = Allergen.objects.get(pk=pk)
            allergen.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Allergen.DoesNotExist:
            return Response({"Error": "Allergen not found."}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(responses={200: AllergenSerializer, 404: "Allergen not found."})
    def retrieve_by_name(self, request, name=None):
        name = turkish_capitalize(name).strip()
        try:
            allergen = Allergen.objects.get(name=name)
            serialized_allergen = AllergenSerializer(allergen)
            return Response(serialized_allergen.data, status=status.HTTP_200_OK)
        except Allergen.DoesNotExist:
            return Response({"Error": "Allergen not found."}, status=status.HTTP_404_NOT_FOUND)


class CommonRegionView(ModelViewSet):
    queryset = CommonRegion.objects.all()
    serializer_class = CommonRegionSerializer

    permission_classes = [FundamentalPermission]
    permission_type = 'view'


class AllergenRegionView(ModelViewSet):
    queryset = AllergenRegion.objects.all()
    serializer_class = AllergenRegionSerializer

    permission_classes = [FundamentalPermission]
    permission_type = 'view'

    @swagger_auto_schema(responses={200: AllergenRegionSerializer, 404: "Allergen not found."})
    def retrieve_by_allergen(self, request, pk=None):
        try:
            allergen = Allergen.objects.get(pk=pk)
            filtered_allergen_regions = AllergenRegion.objects.filter(allergen_id=allergen.id).select_related(
                "common_region")
            common_regions = [allergen_region.common_region for allergen_region in filtered_allergen_regions]
        except Allergen.DoesNotExist:
            return Response({"Error": "Allergen not found."}, status=status.HTTP_404_NOT_FOUND)

        serialized_common_regions = CommonRegionSerializer(common_regions, many=True)
        return Response(serialized_common_regions.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: AllergenRegionSerializer, 404: "Common Region not found."})
    def retrieve_by_region(self, request, pk=None):
        try:
            common_region = CommonRegion.objects.get(pk=pk)
            filtered_allergen_regions = AllergenRegion.objects.filter(common_region_id=common_region.id).select_related(
                "allergen")
            allergens = [allergen_region.allergen for allergen_region in filtered_allergen_regions]
        except CommonRegion.DoesNotExist:
            return Response({"Error": "Common Region not found."}, status=status.HTTP_404_NOT_FOUND)

        serialized_common_regions = CommonRegionSerializer(allergens, many=True)
        return Response(serialized_common_regions.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'common_region_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=['common_region_id']),
        responses={201: AllergenRegionSerializer, 400: "Invalid Data", 404: "Allergen not found."})
    def create(self, request, pk=None):
        try:
            allergen = Allergen.objects.get(pk=pk)
        except Allergen.DoesNotExist:
            return Response({"Error": "Allergen not found."}, status=status.HTTP_404_NOT_FOUND)
        request.data["allergen_id"] = allergen.id

        serializer = AllergenRegionSerializer(data=request.data)
        if serializer.is_valid():
            allergen_region = serializer.save()
            return Response(AllergenRegionSerializer(allergen_region).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'common_region_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=['common_region_id']),
        responses={204: "No Content", 404: "Allergen Region not found.", 400: "common_region_id is required."})
    def destroy(self, request, pk=None):
        common_region_id = request.data.get('common_region_id')

        if not common_region_id:
            return Response({"Error": "common_region_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            allergen = Allergen.objects.get(pk=pk)
            allergen_region = AllergenRegion.objects.get(allergen_id=allergen.id, common_region_id=common_region_id)
            allergen_region.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Allergen.DoesNotExist:
            return Response({"Error": "Allergen not found."}, status=status.HTTP_404_NOT_FOUND)
        except AllergenRegion.DoesNotExist:
            return Response({"Error": "Given Allergen does not contain given Allergen Region."},
                            status=status.HTTP_404_NOT_FOUND)


class UserAllergyView(ModelViewSet):
    queryset = UserAllergy.objects.all()
    serializer_class = UserAllergySerializer

    permission_classes = [FundamentalPermission]
    permission_type = 'crud'

    @swagger_auto_schema(responses={200: UserAllergySerializer(many=True), 404: "User not found."})
    def retrieve_user_allergies(self, request, pk=None):
        try:
            user = AllergicUser.objects.get(pk=pk)
        except AllergicUser.DoesNotExist:
            return Response({"Error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user_allergies = UserAllergy.objects.filter(user_id=user.id)
        serialized_user_allergies = UserAllergySerializer(user_allergies, many=True)
        return Response(serialized_user_allergies.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'allergen_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'importance_level': openapi.Schema(type=openapi.TYPE_INTEGER)
            },
            required=['allergen_id', 'importance_level']),
        responses={201: UserAllergySerializer, 400: "Invalid Data"})
    def create(self, request, pk=None):
        request.data["user_id"] = pk
        serializer = UserAllergySerializer(data=request.data)
        if serializer.is_valid():
            user_allergy = serializer.save()
            return Response(UserAllergySerializer(user_allergy).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={204: "No Content", 404: "User or User Allergy not found"})
    def destroy(self, request, pk=None, user_allergy_id=None):
        try:
            user = AllergicUser.objects.get(pk=pk)
            user_allergy = UserAllergy.objects.get(user=user, id=user_allergy_id)
            user_allergy.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except AllergicUser.DoesNotExist:
            return Response({"Error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except UserAllergy.DoesNotExist:
            return Response({"Error": "User Allergy not found."}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(responses={200: UserAllergySerializer, 404: "User or User Allergy not found."})
    def retrieve_user_allergy(self, request, pk=None, user_allergy_id=None):
        try:
            user = AllergicUser.objects.get(pk=pk)
            user_allergy = UserAllergy.objects.get(user=user, id=user_allergy_id)
            serialized_user_allergy = UserAllergySerializer(user_allergy)
            return Response(serialized_user_allergy.data, status=status.HTTP_200_OK)
        except AllergicUser.DoesNotExist:
            return Response({"Error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except UserAllergy.DoesNotExist:
            return Response({"Error": "User Allergy not found."}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'allergen_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'importance_level': openapi.Schema(type=openapi.TYPE_INTEGER)
            }),
        responses={200: UserAllergySerializer, 400: "Invalid Data", 404: "User or User Allergy not found"})
    def partial_update(self, request, pk=None, user_allergy_id=None):
        try:
            user = AllergicUser.objects.get(pk=pk)
            user_allergy = UserAllergy.objects.get(user=user, id=user_allergy_id)
        except AllergicUser.DoesNotExist:
            return Response({"Error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except UserAllergy.DoesNotExist:
            return Response({"Error": "User Allergy not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserAllergySerializer(user_allergy, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
