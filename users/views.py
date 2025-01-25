from rest_framework.viewsets import ViewSet
from .models import *
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
import rest_framework.status as status
from .serializers import UserSerializer


class UserView(ViewSet):
    @swagger_auto_schema(responses={200: UserSerializer(many=True)})
    def list(self, request):
        allergic_user = AllergicUser.objects.select_related("residence_district").all()
        serialized_allergic_user = UserSerializer(allergic_user, many=True)
        return Response(serialized_allergic_user.data, status=status.HTTP_200_OK)
