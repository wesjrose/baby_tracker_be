from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions  import AllowAny

from .serializers import UserSerializer
# Create your views here.


class UserView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        """
        This endpoint is for creating a new user
        """
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
