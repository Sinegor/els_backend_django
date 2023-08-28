import json

from rest_framework import serializers
from usersApp.models import User, UsersKind, ClientUserInterface, FieldsOfLaw, LawyerUserInterface
from django.db import models
from django.http import HttpResponse, HttpRequest
from django.contrib.auth import authenticate, login, logout
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser


class RegistrationSerializer(serializers.ModelSerializer):

 # Необходимо протестировать с write_only и без. Есть ли разница при таком обозначении или через extra_kwargs
    # password = serializers.CharField(
    #     max_length=128,
    #     min_length=8,
    #     write_only=True
    # )

    
    class Meta:
        model = User
        fields = ['username', 'kind_of_user', 'password', 'email']
        # extra_kwargs = {
        #     'password': {'write_only': True}
        # }
    
    
    def save(self):  
        user = self.create(self.validated_data)
        # User(email=self.validated_data['email'], username = self.validated_data['username'])
        # user.kind_of_user = self.validated_data['kind_of_user']
        password = self.validated_data['password']
        user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    def user_authenticate(self, request):
        username = self.validated_data['username']
        password = self.validated_data['password']
        user = authenticate(request, username=username, password=password)
        return user
  

class ClientInterfaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientUserInterface
        fields = ['full_name', 'phone', 'user_name', 'payment_method']

        extra_kwargs = {
            'payment_method':{
                'default':''
            }
        } 

    def save(self):
        client = ClientUserInterface(full_name = self.validated_data['full_name'],
                                     phone = self.validated_data['phone'],
                                     user_name = self.validated_data['user_name'],
                                     )
        client.save()
        return client
    def split_fullname(self):
        full_name:str = self.validated_data['full_name']
        first_name, last_name = full_name.split(' ')[0], full_name.split(' ')[1]
        current_user:User = self.validated_data['user_name']
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.save()
    def check_user(self):
        current_user:User = self.validated_data['user_name']
        if current_user.kind_of_user==UsersKind.objects.get(pk=2):
            return False
        elif current_user.kind_of_user==None:
            current_user.kind_of_user==UsersKind.objects.get(pk=1)
        current_user.kind_of_user==UsersKind.objects.get(pk=1)
        return True
        

class LawyerUserInterfaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LawyerUserInterface
        fields = ['full_name', 'phone', 'user_name', 'preferred_location',
                  'preferred_location', 'current_city']

    def save (self):
        cur_lawyer = LawyerUserInterface(full_name = self.validated_data['full_name'],
                                        phone = self.validated_data['phone'],
                                        user_name = self.validated_data['user_name'],
                                        preferred_location = self.validated_data['preferred_location'],
                                        current_city = self.validated_data['current_city'],
                                        )
        cur_lawyer.save()
        return cur_lawyer 

    def split_fullname(self):
        full_name:str = self.validated_data['full_name']
        first_name, last_name = full_name.split(' ')[0], full_name.split(' ')[1]
        current_user:User = self.validated_data['user_name']
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.save()  
    
    def check_actual_law (self, law_data:dict):
        # надо как-то закешировать актуальные области права:
        crud_data = FieldsOfLaw.objects.values('area').all()
        actual_law = []
        for data in crud_data:
            actual_law.append(data['area'])
        for type_of_law in law_data:
            for law in law_data[type_of_law]:
                if law not in actual_law:
                    raise serializers.ValidationError ('Вы указали недопустимую область права')      
        return True

    
    def create_law_profile (self, inst_interface:LawyerUserInterface, data):
        law_data=FieldsOfLaw.objects.all()
        specialization_data = data['specialization']
        incompetence_data = data['incompetence']
        used_values = []
        for type_law in incompetence_data:
            for area in incompetence_data[type_law]:
                inst_interface.incompetence.add(law_data.get(area=area))
                used_values.append(area)
        for type_law in specialization_data:
            for area in specialization_data[type_law]:
                if area in used_values:
                    inst_interface.delete()
                    raise serializers.ValidationError('Error. Right fields in specialization and incompetence cannot be the same')      
                inst_interface.specialization.add(law_data.get(area=area))
        inst_interface.save()    
        return inst_interface
    
    
    def check_user(self):
        current_user:User = self.validated_data['user_name']
        if current_user.kind_of_user==UsersKind.objects.get(pk=1):
            return False
        elif current_user.kind_of_user==None:
            current_user.kind_of_user==UsersKind.objects.get(pk=2)
        return True

        
  

class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={"input_type": "password"}, required=True)
    new_password = serializers.CharField(style={"input_type": "password"}, required=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError({'current_password': 'Does not match'})
        return value

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email',]
        

class UpdateClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientUserInterface
        fields = ['full_name', 'phone', 'payment_method' ]
        extra_kwargs= {
            'full_name':{
                'required':False,
            },   
            'phone':{
                'required':False,
            },   
        }
    def split_fullname(self, user):
        full_name:str = self.validated_data['full_name']
        first_name, last_name = full_name.split(' ')[0], full_name.split(' ')[1]
        user.first_name = first_name
        user.last_name = last_name
        user.save()

class UpdateLawyerSerializer(serializers.ModelSerializer):
    class Meta:
        model = LawyerUserInterface
        fields = ['full_name', 'phone', 'payment_method', 'preferred_location',
                  'current_city', 'current_location']
        extra_kwargs= {
            'full_name':{
                'required':False,
            },   
            'phone':{
                'required':False,
            },  
            'current_city':{
                'required':False,
            },
            'preferred_location':{
                'required':False,
            },

        }   
    def split_fullname(self, user):
        full_name:str = self.validated_data['full_name']
        first_name, last_name = full_name.split(' ')[0], full_name.split(' ')[1]
        user.first_name = first_name
        user.last_name = last_name
        user.save()
    
    def create_specialization(self, inst_interface:LawyerUserInterface, data_specialization):
        #data_specialization = json.loads(data)
        for type_law in data_specialization:
            for area in data_specialization[type_law]:
                current_specialization = FieldsOfLaw.objects.get(area=area)
                inst_interface.specialization.add(current_specialization)
        return inst_interface
    
    def create_incompetence(self, inst_interface:LawyerUserInterface, data_incompetence):
        for type_law in data_incompetence:
            for area in data_incompetence[type_law]:
                current_incompetence = FieldsOfLaw.objects.get(area=area)
                inst_interface.incompetence.add(current_incompetence)
        return inst_interface

class ReadUserSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ['username', 'first_name', 'last_name', 'email',
                  'date_joined', 'last_login', 'is_superuser', 'is_staff', 'kind_of_user']

class ReadClientSerializer(serializers.ModelSerializer):
    class Meta():
        model = ClientUserInterface
        fields = ['user_name', 'full_name', 'phone', 'payment_method',
                  'current_requests', 'history_of_requests']

class ReadLawyerSerializer(serializers.ModelSerializer):
    class Meta():
        model = LawyerUserInterface
        exclude= ['name_of_interface',]
        
    full_name = serializers.CharField()
    user_name = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username')
    specialization = serializers.SlugRelatedField(many=True, read_only=True, slug_field='area')
    incompetence = serializers.SlugRelatedField(many=True, read_only=True, slug_field='area')
 
# class ReadLawyerSerializer(serializers.Serializer):
#     full_name = serializers.CharField()
    
    