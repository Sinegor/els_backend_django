
import time

from django.http import HttpResponse, HttpRequest
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.contrib.auth.decorators import login_required



from rest_framework import status, authentication, serializers, permissions
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import  Response
from rest_framework.renderers import JSONRenderer

from usersApp.models import User, LawyerUserInterface, ClientUserInterface, FieldsOfLaw
from usersApp.serializers import RegistrationSerializer, PasswordChangeSerializer,\
                                 ClientUserInterfaceSerializer, LoginSerializer, LawyerUserInterfaceSerializer,\
                                UpdateLawyerSerializer
                                 #UpdateUserSerializer, UpdateClientSerializer,

from usersApp.utils import get_tokens_for_user
from usersApp.autth_methods import push_auth_email
from ela_backend.settings import SIGNING_KEY



class RegistrationView(APIView):

    permission_classes = (AllowAny,)
    def post(self, request:HttpRequest):  
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
#            push_auth_email(serializer.validated_data['email'], serializer.validated_data['username'])
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
    permission_classes = [IsAuthenticated, ]
    def post(self, request:HttpRequest):
        my_data = request.data
        current_user = request.user
        my_data['user_name']= current_user
        serializer = ClientUserInterfaceSerializer(data=my_data)
        if serializer.is_valid():
            if serializer.check_user():
                serializer.save()
#                serializer.create(serializer.validated_data)
                serializer.check_fullname(my_data, current_user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response ("Данный пользователь уже является юристом и не может быть зарегистрирован в качестве клиента", 
                             status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegistrationLawyerView(APIView):
    permission_classes = [IsAuthenticated, ]
    def post(self, request:HttpRequest):
        my_data = request.data
        if not 'specialization' in my_data or not 'incompetence' in my_data:
            return Response('Отсутствует необходимые данные о компетенции',
                            status=status.HTTP_400_BAD_REQUEST)
        my_data['user_name']= request.user
        serializer =  LawyerUserInterfaceSerializer(data=my_data)
        if serializer.is_valid():
            actual_law_dict = FieldsOfLaw.get_actual_law()
            if serializer.check_user() and serializer.check_law_data_request(my_data, actual_law_dict):
                serializer.split_fullname()    
                crud_lawyer = serializer.create(serializer.validated_data)
                serializer.create_law_profile(crud_lawyer, my_data)
                return Response(f'{serializer.data}', status=status.HTTP_201_CREATED)
            return Response (f"{request.user}: Данный пользователь уже является клиентом и не может быть зарегистрирован в качестве юриста",
                                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegistrationConfirmEmailView(APIView):
    def get(self, request:HttpRequest, user):
        current_user = User.objects.get(username=user)
        current_user.email_confirm = True
        current_user.save()
        return Response('Email confirmed', status=status.HTTP_200_OK)

class UpdateUserView(APIView):
    permission_classes = [IsAuthenticated, ]
    def post(self, request:HttpRequest,):
        """
        With this route, user can change their email address. 
        Admin can change mail from any user
        """
        current_user = request.user
        my_data:dict = request.data
        serializer = RegistrationSerializer(data=my_data)
        if not my_data.get('username') or my_data.get('username') == current_user.username:
            if serializer.is_valid():    
                serializer.update(current_user, serializer.validated_data)
                push_auth_email(serializer.validated_data['email'], current_user.username)
                return Response ('User updated sucsesfull', status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif current_user.is_staff == True:
            if serializer.is_valid():    
                updaiting_user = User.objects.get(username=my_data['user'])
                serializer.update(updaiting_user, serializer.validated_data)
                push_auth_email(serializer.validated_data['email'], my_data['user'])
                return Response ('User updated sucsesfull', status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('Для изменения данных этого юзера у вас отсутствуют полномочия',
                             status=status.HTTP_400_BAD_REQUEST)



class UpdateClientView(APIView):
    permission_classes = [IsAuthenticated, ]
    def post(self, request:HttpRequest):
        """
        With this route, user can change their client_interface. 
        Admin can change any client_interface. 
        """
        my_data:dict = request.data
        current_user = request.user
        current_client:ClientUserInterface = getattr(current_user, 'client_user_interface', 'nobody')
        if current_client == 'nobody' and not my_data.get('client_id', False):
            return Response('You have not provided information about the customer whose profile you want to change',
                            status=status.HTTP_400_BAD_REQUEST)
        elif (current_client !='nobody' and not my_data.get('client_id', False)) or (current_client !='nobody' and current_client.pk == my_data.get('client_id', False)):
            if not request.data.get('full_name', False):
                my_data['full_name'] = current_client.full_name
            if not request.data.get('phone', False):
                my_data['phone'] = current_client.phone
            if not request.data.get('user_name', False):
                my_data['user_name'] = current_client.user_name
            if not request.data.get('name_of_interface', False):
                    my_data['name_of_interface']= current_client.name_of_interface.pk


            serializer = ClientUserInterfaceSerializer(data=my_data)
            if serializer.is_valid():
                serializer.update(current_client, serializer.validated_data)
                serializer.check_fullname(serializer.validated_data, current_user)
                return Response ('Client interface updated sucsesfull', status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            if current_user.is_staff == True:
                updaiting_client = ClientUserInterface.objects.get(pk=my_data.get('client_id'))
                if not request.data.get('full_name', False):
                    my_data['full_name'] = updaiting_client.full_name
                if not request.data.get('phone', False):
                    my_data['phone'] = updaiting_client.phone
                if not request.data.get('user_name', False):
                    my_data['user_name'] = updaiting_client.user_name
                if not request.data.get('name_of_interface', False):
                    my_data['name_of_interface']= updaiting_client.name_of_interface.pk

                serializer = ClientUserInterfaceSerializer(data=my_data)
                if serializer.is_valid():    
                    serializer.update(updaiting_client, serializer.validated_data)
                    serializer.check_fullname(serializer.validated_data, updaiting_client.user_name)
                    return Response ('Client interface updated sucsesfull', status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response('Для изменения данных этого юзера у вас отсутствуют полномочия',
                             status=status.HTTP_400_BAD_REQUEST)

        
    
class UpdateLawyerView(APIView):
    
    permission_classes = [IsAuthenticated, ]    
    def post(self, request:HttpRequest):
        my_data:dict = request.data
        current_user = request.user
        current_lawyer:LawyerUserInterface = getattr(current_user, 'lawyer_user_interface', 'nobody')
        serializer = UpdateLawyerSerializer(data=my_data)
        if current_lawyer == 'nobody' and not my_data.get('lawyer_id', False):
            return Response('You have not provided information about the lawyer whose profile you want to change',
                            status=status.HTTP_400_BAD_REQUEST)
        actual_law_list = FieldsOfLaw.get_actual_law()
        if (current_lawyer !='nobody' and not my_data.get('lawyer_id', False)) or (current_lawyer !='nobody' and current_lawyer.pk == my_data.get('lawyer_id', False)):
            if serializer.is_valid():
                serializer.update(current_lawyer, serializer.validated_data)
                serializer.check_fullname(serializer.validated_data, current_user)
                serializer.check_law_data_request(current_lawyer, my_data, actual_law_list)
                return Response ('Lawyer interface updated sucsesfull', status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif current_user.is_staff == True:
            if serializer.is_valid():    
                updaiting_lawyer = LawyerUserInterface.objects.get(pk=my_data.get('lawyer_id'))
                serializer.update(updaiting_lawyer, serializer.validated_data)
                serializer.check_fullname(serializer.validated_data, updaiting_lawyer.user_name)
                serializer.check_law_data_request(updaiting_lawyer, my_data, actual_law_list)
                return Response ('Lawyer interface updated sucsesfull', status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('Для изменения данных этого юзера у вас отсутствуют полномочия',status=status.HTTP_400_BAD_REQUEST )

              
class ReadUserView(APIView):
    permission_classes = [IsAuthenticated, ]
    def get(self, request:HttpRequest):
        current_user = request.user
        if request.GET.get('user_id', False):
            if current_user.is_staff or current_user.pk == int(request.GET['user_id']):
                requested_user = User.objects.get(pk=request.GET['user_id'])
                serializer = RegistrationSerializer(requested_user)
                response= serializer.data
                [print(f'{key}: {response[key]}\n') for key in response]
                return Response (response, status=status.HTTP_200_OK)
            else:

                return Response('Для просмотра данных этого юзера у вас отсутствуют полномочия', status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = RegistrationSerializer(current_user)
            response = serializer.data
            return Response (response, status=status.HTTP_200_OK)

class ReadClientView(APIView):
    permission_classes = [IsAuthenticated, ]
    def get (self, request:HttpRequest):
        current_user = request.user
        current_client:ClientUserInterface = getattr(current_user, 'client_user_interface', 'nobody')
        if current_client == 'nobody' and not request.GET.get('client_id', False):
            return Response('You have not provided information about the customer whose profile you want to change',
                            status=status.HTTP_400_BAD_REQUEST)
        elif (current_client !='nobody' and not request.GET.get('client_id', False)) or (current_client !='nobody' and current_client.pk == int(request.GET.get('client_id', False))):
            serializer = ClientUserInterfaceSerializer(current_client)
            response = serializer.data
            return Response (response, status=status.HTTP_201_CREATED)
        else:
            if current_user.is_staff == True:
                requesting_client = ClientUserInterface.objects.get(pk= request.GET.get('client_id', False))
                serializer = ClientUserInterfaceSerializer(requesting_client)
                
                return Response (serializer.data, status=status.HTTP_201_CREATED)
                
            return Response('Для чтения данных этого клиента у вас отсутствуют полномочия',
                             status=status.HTTP_400_BAD_REQUEST)


class ReadLawyerView(APIView):
    ...
    # permission_classes = [IsAuthenticated, ]
    # def get (self, request:HttpRequest):
    #     current_user = request.user
        
    #     current_lawyer = current_user.lawyer_user_interface
    #     serializer = ReadLawyerSerializer(current_lawyer)
    #     response= serializer.data
    #     [print(f'{key}: {response[key]}\n') for key in response]
    #     return Response (response, status=status.HTTP_200_OK)

class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated, ]
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
    permission_classes = (permissions.IsAuthenticated)
    def get (self, request:HttpRequest):
                
        print(request.auth)
        return Response('ok', status=status.HTTP_200_OK)
        



            


