import io
import json
import time

from django.http import HttpResponse, HttpRequest
from django.db import models
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.contrib.auth.decorators import login_required



from rest_framework import status, authentication, serializers
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import  Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from usersApp.models import User, UsersKind, ClientUserInterface, LawyerUserInterface
from usersApp.serializers import RegistrationSerializer, PasswordChangeSerializer,\
                                 ClientInterfaceSerializer, LoginSerializer, LawyerUserInterfaceSerializer,\
                                 UpdateUserSerializer, UpdateClientSerializer, UpdateLawyerSerializer,\
                                 ReadUserSerializer, ReadClientSerializer, ReadLawyerSerializer

from usersApp.utils import get_tokens_for_user
from usersApp.autth_methods import push_auth_email



class RegistrationView(APIView):
# permission_classes устанавливает, для кого доступен данный ендпоинт, в данном случае для всех.
    permission_classes = (AllowAny,)
    def post(self, request:HttpRequest):  
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            push_auth_email(serializer.validated_data['email'], serializer.validated_data['username'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request:HttpRequest):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.user_authenticate(request)
            if user is not None:
                login(request, user)
                auth_data = get_tokens_for_user(request.user)
                return Response({'msg': 'Login Success', **auth_data}, status=status.HTTP_200_OK) 
            return Response({'msg':'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)    
        return HttpResponse({'msg':'Credentials missing'}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated, ]
    def post(self, request):
        logout(request)
        return Response({'msg': 'Successfully Logged out'}, status=status.HTTP_200_OK)

      
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated, ]
    def post(self, request):
        serializer = PasswordChangeSerializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True) #Another way to write is as in Line 33
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class RegistrationClientView(APIView):
    
    def post(self, request:HttpRequest):
        my_data = request.data
        current_user = request.user
        my_data['user_name']= current_user
        serializer = ClientInterfaceSerializer(data=my_data)
        if serializer.is_valid():
            if serializer.check_user():
                serializer.save()
                serializer.split_fullname()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response ("Данный пользователь уже является юристом и не может быть зарегистрирован в качестве клиента", 
                             status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegistrationLawyerView(APIView):
    def post(self, request:HttpRequest):
        my_time = time.time()
        my_data = request.data
        if not 'specialization' in my_data or not 'incompetence' in my_data:
            return Response('Отсутствует необходимые данные о компетенции',
                            status=status.HTTP_400_BAD_REQUEST)
        my_data['user_name']= request.user
        serializer =  LawyerUserInterfaceSerializer(data=my_data)
        if serializer.is_valid():
            if serializer.check_user() and serializer.check_actual_law(my_data['specialization'])\
                                       and serializer.check_actual_law(my_data['incompetence']):
                serializer.split_fullname()    
                crud_lawyer = serializer.save()
                serializer.create_specialization(crud_lawyer, my_data['specialization'])
                serializer.create_incompetence(crud_lawyer, my_data['incompetence'])
                return Response(f'{time.time()- my_time}/n{serializer.data}', status=status.HTTP_201_CREATED)
            return Response (f"{time.time()- my_time}/n {serializer.data}Данный пользователь уже является клиентом и не может быть зарегистрирован в качестве юриста",
                                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegistrationConfirmEmailView(APIView):
    def get(self, request:HttpRequest, user):
        current_user = User.objects.get(username=user)
        current_user.email_confirm = True
        current_user.save()
        return Response('Email confirmed', status=status.HTTP_200_OK)

class GetCurrentUserView (APIView):
    def get (self, request:HttpRequest):
        cur_user = request.user
        print (cur_user.is_authenticated)
        my_session = request.session
        print(my_session)
        return Response ('ok')

class UpdateUserView(APIView):
    def post(self, request:HttpRequest):
        my_data = request.data
        serializer = UpdateUserSerializer(data=my_data)
        if serializer.is_valid():
            current_user = request.user
            serializer.update(current_user, serializer.validated_data)
            push_auth_email(serializer.validated_data['email'], current_user.username)
            return Response ('User updated sucsesfull', status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateClientView(APIView):
    def post(self, request:HttpRequest):
        my_data = request.data
        serializer = UpdateClientSerializer(data=my_data)
        if serializer.is_valid():
            current_user = request.user
            current_client = current_user.client_user_interface
            serializer.update(current_client, serializer.validated_data)
            if 'full_name' in serializer.validated_data:
                serializer.split_fullname(current_user)
            return Response ('Client interface updated sucsesfull', status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UpdateLawyerView(APIView):
    def post(self, request:HttpRequest):
        my_data = request.data
        serializer = UpdateLawyerSerializer(data=my_data)
        if serializer.is_valid():
            current_user = request.user
            current_lawyer:LawyerUserInterface = current_user.lawer_user_interface
            serializer.update(current_lawyer, serializer.validated_data)
            if 'full_name' in serializer.validated_data:
                serializer.split_fullname(current_user)
            if 'incompetence' in my_data:
                current_lawyer.incompetence.clear()    
                incompetence_data = my_data['incompetence']
                serializer.create_incompetence(current_lawyer, incompetence_data)
            if 'specialization' in my_data:
                specialization_data = my_data['specialization']
                current_lawyer.specialization.clear()
                serializer.create_specialization(current_lawyer, specialization_data)
            return Response ('Lawyer interface updated sucsesfull', status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReadUserView(APIView):
    def get(self, request:HttpRequest):
        current_user = request.user
        serializer = ReadUserSerializer(current_user)
        response= serializer.data
        [print(f'{key}: {response[key]}\n') for key in response]
        return Response (response, status=status.HTTP_200_OK)

class ReadClientView(APIView):
    def get (self, request:HttpRequest):
        current_user = request.user
        current_client = current_user.client_user_interface
        serializer = ReadClientSerializer(current_client)
        response= serializer.data
        [print(f'{key}: {response[key]}\n') for key in response]
        return Response (response, status=status.HTTP_200_OK)

class ReadLawyerView(APIView):
    def get (self, request:HttpRequest):
        current_user = request.user.username    
        current_lawyer = current_user.lawer_user_interface
        serializer = ReadLawyerSerializer(current_lawyer)
        response= serializer.data
        [print(f'{key}: {response[key]}\n') for key in response]
        return Response (response, status=status.HTTP_200_OK)

class DeleteUserView(APIView):
    def delete (self, request:HttpRequest,):
        current_user_name = request.user.username
        if (current_user_name == request.GET['delete_username']) or (request.user.is_superuser == True):
            current_user = User.objects.get(username=current_user_name)
            current_user.is_active = False
            current_user.save()
            return Response('Uninstalled successfully', status=status.HTTP_200_OK)
        else:
            return Response ('There are no permissions to remove this user', status= status.HTTP_400_BAD_REQUEST)


class TestingView(APIView):
    ... # def get (self, request):
    #     result = get_list_of_law()
    #     print (type(result))
    #     print (result)
    #     return Response ('Ok', status=status.HTTP_200_OK)

        



            


