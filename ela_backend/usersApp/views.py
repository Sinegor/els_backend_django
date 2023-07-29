from django.http import HttpResponse, HttpRequest
from django.db import models
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from rest_framework import status, authentication
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import  Response
from rest_framework.request import Request
from rest_framework.views import APIView




from usersApp.models import User, UsersKind, ClientUserInterface, LawyerUserInterface
from usersApp.serializers import RegistrationSerializer, PasswordChangeSerializer, ClientInterfaceSerializer
from usersApp.utils import get_tokens_for_user

class RegistrationView(APIView):
# permission_classes устанавливает, для кого доступен данный ендпоинт, в данном случае для всех.
    permission_classes = (AllowAny,)
    def post(self, request:HttpRequest):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request:HttpRequest):
        if 'username' not in request.data or 'password' not in request.data:
            return HttpResponse({'msg': 'Credentials missing'}, status=status.HTTP_400_BAD_REQUEST)
        username = request.data['username']
        password = request.data['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            auth_data = get_tokens_for_user(request.user)
            # my_response = Response({'msg': 'Login Success', **auth_data}, status=status.HTTP_200_OK)
            # my_response.set_cookie('Authorization', auth_data['access'])
            return Response({'msg': 'Login Success', **auth_data}, status=status.HTTP_200_OK)
            #return my_response
        return Response({'msg': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)



class LogoutView(APIView):
    permission_classes = [IsAuthenticated, ]
    def post(self, request):
        logout(request)
        return Response({'msg': 'Successfully Logged out'}, status=status.HTTP_200_OK)


      
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated, ]
    def post(self, request):
        serializer = PasswordChangeSerializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True) #Another way to write is as in Line 17
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class GetCurrentUser (APIView):
    def get (self, request:Request):
        cur_user = request.user()
        print (cur_user)
        return Response (cur_user)
    
class RegistrationClientView(APIView):
    #permission_classes = [IsAuthenticated, ]
    def post(self, request:HttpRequest):
        my_data = request.data
        current_user = request.user
        my_data['user_name']= current_user
        serializer = ClientInterfaceSerializer(data=my_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

