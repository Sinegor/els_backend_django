from rest_framework import serializers
from usersApp.models import User, UsersKind, ClientUserInterface
from django.db import models
from django.http import HttpResponse, HttpRequest
from django.contrib.auth import authenticate, login, logout
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
class RegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'kind_of_user', 'password', 'email']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    
    def save(self):  
        user = self.create(self.validated_data)
        # User(email=self.validated_data['email'], username = self.validated_data['username'])
        # user.kind_of_user = self.validated_data['kind_of_user']
        password = self.validated_data['password']
        user.set_password(password)
        user.save()
        return user

class ClientInterfaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientUserInterface
        fields = ['full_name', 'phone', 'user_name', ]
    def save(self):
        client = ClientUserInterface(full_name = self.validated_data['full_name'],
                                     phone = self.validated_data['phone'],
                                     user_name = self.validated_data['user_name'],
                                     )
        client.save()
        full_name:str = self.validated_data['full_name']
        first_name, last_name = full_name.split(' ')[0], full_name.split(' ')[1]
        current_user:User = self.validated_data['user_name']
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.save()
        return client
        
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    def user_authenticate(self, request):
        username = self.validated_data['username']
        password = self.validated_data['password']
        user = authenticate(request, username=username, password=password)
        return user
    

class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={"input_type": "password"}, required=True)
    new_password = serializers.CharField(style={"input_type": "password"}, required=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError({'current_password': 'Does not match'})
        return value