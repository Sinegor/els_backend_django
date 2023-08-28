from django.http import HttpResponse, HttpRequest
from django.core.exceptions import ValidationError

from rest_framework import status, authentication, serializers, permissions
from rest_framework.views import APIView
from rest_framework.response import  Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from legalApplication.serializers import CreateLegalAppSerializer
from usersApp.models import User


class CreateLegalApp (APIView):
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

        