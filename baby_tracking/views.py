from django.shortcuts import render

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import BabySerializer
from .models import GuardianMapping

# Create your views here.

# TODO: create baby



# TODO: add user to the baby (will need tokenized version to check)


class UserView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """This is the endpoint for creating a new baby. The baby will be 
        assigned to the user that creates the baby.
        """

        serializer = BabySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        baby = serializer.save()

        GuardianMapping.objects.create(baby=baby, guardian=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    