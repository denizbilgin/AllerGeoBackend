from rest_framework.viewsets import ModelViewSet, ViewSet
from .models import *
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
import rest_framework.status as status
from drf_yasg import openapi
from AllerGeoBackend.utilities import turkish_capitalize


class AllergenTypeView(ModelViewSet):
    queryset = AllergenType.objects.all()
    serializer_class = AllergenTypeSerializer

    @swagger_auto_schema(responses={200: AllergenSerializer(many=True), 404: "Allergen Type not found."})
    def retrieve_allergens_by_type(self, request, pk=None):
        try:
            allergen_type = AllergenType.objects.get(pk=pk)
        except AllergenType.DoesNotExist:
            return Response({"error": "Allergen Type not found."}, status=status.HTTP_404_NOT_FOUND)

        items = Allergen.objects.filter(allergen_type=allergen_type)
        serialized_items = AllergenSerializer(items, many=True)
        return Response(serialized_items.data, status=status.HTTP_200_OK)


class AllergenView(ViewSet):
    @swagger_auto_schema(responses={200: AllergenSerializer(many=True)})
    def list(self, request):
        items = Allergen.objects.all()
        serialized_items = AllergenSerializer(items, many=True)
        return Response(serialized_items.data, status=status.HTTP_200_OK)

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
            serialized_item = AllergenSerializer(allergen)
            return Response(serialized_item.data, status=status.HTTP_200_OK)
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
        responses={201: AllergenSerializer, 400: "Invalid Data"})
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
            serialized_item = AllergenSerializer(allergen)
            return Response(serialized_item.data, status=status.HTTP_200_OK)
        except Allergen.DoesNotExist:
            return Response({"Error": "Allergen not found."}, status=status.HTTP_404_NOT_FOUND)


class CommonRegionView(ModelViewSet):
    queryset = CommonRegion.objects.all()
    serializer_class = CommonRegionSerializer


class AllergenRegionView(ViewSet):
    @swagger_auto_schema(responses={200: AllergenRegionSerializer, 404: "Allergen not found."})
    def retrieve_by_allergen(self, request, pk=None):
        try:
            item = Allergen.objects.get(pk=pk)
            items = AllergenRegion.objects.filter(allergen_id=item.id).select_related("common_region")
            common_regions = [item.common_region for item in items]
        except Allergen.DoesNotExist:
            return Response({"Error": "Allergen not found."}, status=status.HTTP_404_NOT_FOUND)

        serialized_items = CommonRegionSerializer(common_regions, many=True)
        return Response(serialized_items.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: AllergenRegionSerializer, 404: "Common Region not found."})
    def retrieve_by_region(self, request, pk=None):
        try:
            item = CommonRegion.objects.get(pk=pk)
            items = AllergenRegion.objects.filter(common_region_id=item.id).select_related("allergen")
            allergens = [item.allergen for item in items]
        except CommonRegion.DoesNotExist:
            return Response({"Error": "Common Region not found."}, status=status.HTTP_404_NOT_FOUND)

        serialized_items = CommonRegionSerializer(allergens, many=True)
        return Response(serialized_items.data, status=status.HTTP_200_OK)

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
            return Response({"Error": "Given Allergen does not contain given Allergen Region."}, status=status.HTTP_404_NOT_FOUND)


class UserAllergyView(ViewSet):
    @swagger_auto_schema(responses={200: UserAllergySerializer(many=True), 404: "User not found."})
    def retrieve_user_allergies(self, request, pk=None):
        try:
            user = AllergicUser.objects.get(pk=pk)
        except AllergicUser.DoesNotExist:
            return Response({"Error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user_allergies = UserAllergy.objects.filter(user_id=user.id)
        serialized_items = UserAllergySerializer(user_allergies, many=True)
        return Response(serialized_items.data, status=status.HTTP_200_OK)

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

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'allergen_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=['allergen_id']),
        responses={204: "No Content", 404: "Allergen or User not found.", 400: "common_region_id is required."})
    def destroy(self, request, pk=None):
        allergen_id = request.data.get('allergen_id')
        try:
            user = AllergicUser.objects.get(pk=pk)
            allergen = Allergen.objects.get(pk=allergen_id)
            user_allergy = UserAllergy.objects.get(user=user, allergen=allergen)
            user_allergy.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except AllergicUser.DoesNotExist:
            return Response({"Error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Allergen.DoesNotExist:
            return Response({"Error": "Allergen not found."}, status=status.HTTP_404_NOT_FOUND)
        except UserAllergy.DoesNotExist:
            return Response({"Error": "User Allergy not found."}, status=status.HTTP_404_NOT_FOUND)


class AllergyAttackView(ViewSet):
    @swagger_auto_schema(responses={200: AllergyAttackSerializer(many=True), 404: "User not found."})
    def retrieve_user_allergy_attacks(self, request, pk=None):
        try:
            user = AllergicUser.objects.get(pk=pk)
        except AllergicUser.DoesNotExist:
            return Response({"Error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user_allergy_attacks = AllergyAttack.objects.filter(user=user)
        serialized_items = AllergyAttackSerializer(user_allergy_attacks, many=True)
        return Response(serialized_items.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'district_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME,
                                       description="Date and time in ISO 8601 format (e.g., 2025-01-05T14:30:00Z)"),
                "allergen_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "notes": openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['district_id', 'date', "allergen_id"]),
        responses={201: AllergyAttackSerializer, 400: "Invalid Data"})
    def create(self, request, pk=None):
        request.data["user_id"] = pk
        serializer = AllergyAttackSerializer(data=request.data)
        if serializer.is_valid():
            user_allergy_attack = serializer.save()
            return Response(AllergyAttackSerializer(user_allergy_attack).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'district_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME,
                                       description="Date and time in ISO 8601 format (e.g., 2025-01-05T14:30:00Z)"),
                "allergen_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "notes": openapi.Schema(type=openapi.TYPE_STRING)
            }),
        responses={201: AllergyAttackSerializer, 400: "Invalid Data"})
    def partial_update(self, request, pk=None, allergy_attack_id=None):
        try:
            user = AllergicUser.objects.get(pk=pk)
            allergy_attack = AllergyAttack.objects.get(pk=allergy_attack_id, user=user)
        except AllergicUser.DoesNotExist:
            return Response({"Error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except AllergyAttack.DoesNotExist:
            return Response({"Error": "Allergy Attack not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AllergyAttackSerializer(allergy_attack, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={204: "No Content", 404: "User or Allergy Attack not found"})
    def destroy(self, request, pk=None, allergy_attack_id=None):
        try:
            user = AllergicUser.objects.get(pk=pk)
            allergen_attack = AllergyAttack.objects.get(user=user, pk=allergy_attack_id)
            allergen_attack.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except AllergicUser.DoesNotExist:
            return Response({"Error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except AllergyAttack.DoesNotExist:
            return Response({"Error": "Allergy Attack not found."}, status=status.HTTP_404_NOT_FOUND)
