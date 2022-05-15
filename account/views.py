from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .serializers import UserSerializer
from .models import User

# Create your views here.
class SignUp(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user: User = serializer.save()
            # CustomURL Manager 그룹이 사전에 정의되어 있어야 함
            user.groups.add(Group.objects.get(name='CustomURL Manager'))
            return Response("Signup Success", status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignIn(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            username = request.data["username"]
            password = request.data["password"]
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return Response("Signin Success", status=status.HTTP_200_OK)
            else:
                return Response("Signin Failed", status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Signin Failed", status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):

    def post(self, request):
        try:
            logout(request)
            return Response("Logout Success", status=status.HTTP_200_OK)
        except:
            return Response("Logout Failed", status=status.HTTP_400_BAD_REQUEST)
