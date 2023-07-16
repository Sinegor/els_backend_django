from rest_framework.views import APIView
from django.http import HttpResponse
from django.db import models
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import  Response
from rest_framework.views import APIView

from usersApp.models import User, UsersKind, ClientUserInterface, LawyerUserInterface
from usersApp.serializers import RegistrationSerializer

class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        # user = User(email=request.data['userMail'], username = request.data['login'])
        # user.kind_of_user = UsersKind.objects.get(id=int(request.data['userKind']))
        # password = request.data['password']
        # user.set_password(password)
        # user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return (Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST))
  


      


class LoginView(APIView):
    ...

class LogoutView(APIView):
    ...

class ChangePasswordView(APIView):
    ...
