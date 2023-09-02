from django.http import HttpResponse, HttpRequest
from django.core.exceptions import ValidationError

from rest_framework import status, authentication, serializers, permissions
from rest_framework.views import APIView
from rest_framework.response import  Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from legalApplication.serializers import CreateLegalAppSerializer, ReadLegalAppSerializer
from usersApp.models import User
from legalApplication.models import LegalApp


class CreateLegalAppView (APIView):
    permission_classes = [IsAuthenticated,]
    def post (self, request:HttpRequest):
        my_data = request.data
        current_user:User = request.user
        if hasattr(current_user, 'client_user_interface'):
            #my_data['client'] = current_user.username
            my_data['client'] = current_user.client_user_interface.pk
            serializer = CreateLegalAppSerializer(data=my_data)
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response (serializer.data, status=status.HTTP_201_CREATED)
                except ValidationError as e:
                    return Response (e.message, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('This user is registered as a lawyer and cannot be a client',
                        status=status.HTTP_400_BAD_REQUEST)

class UpdateLegalAppView (APIView):
    ...

class ReadLegalAppView(APIView):
    #permission_classes = [IsAuthenticated,]
    def get (self, request:HttpRequest):
        """
        At the moment it is possible to get superuser full information about any application. 
        Clients and lawyers can get data only on their applications

        """
        id_app = request.GET['app_id']
        cur_user = request.user
        if cur_user.is_superuser or cur_user.is_staff:
            cur_legal_app = LegalApp.objects.get(pk=id_app)
            serializer = ReadLegalAppSerializer(cur_legal_app)
            response = serializer.data
            [print(f'{key}: {response[key]}\n') for key in response]
            return Response (response, status=status.HTTP_200_OK)
        else:
            cur_legal_app = LegalApp.objects.get(pk=id_app)
            if (hasattr(cur_user, 'client_user_interface') and cur_user.client_user_interface == cur_legal_app.client) or\
                (hasattr(cur_user, 'lawyer_user_interface') and cur_user.lawyer_user_interface == cur_legal_app.lawyer):
                serializer = ReadLegalAppSerializer(cur_legal_app)
                response = serializer.data
                [print(f'{key}: {response[key]}\n') for key in response]
                return Response (response, status=status.HTTP_200_OK)
            else:
                return Response ('You dont have permission for read this app', status=status.HTTP_400_BAD_REQUEST)

            
        



class DeleteLegalAppView(APIView):
    ...

