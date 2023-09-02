import json

from rest_framework import serializers
from usersApp.models import User, UsersKind, ClientUserInterface, FieldsOfLaw, LawyerUserInterface
from django.db import models
from django.http import HttpResponse, HttpRequest
from django.contrib.auth import authenticate, login, logout
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

class RegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'kind_of_user', 'password', 'email']
        write_only_fields = ['password',]
         
    
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
    password = serializers.CharField(write_only=True)
    def user_authenticate(self, request):
        username = self.validated_data['username']
        password = self.validated_data['password']
        user = authenticate(request, username=username, password=password)
        return user
  

class ClientInterfaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientUserInterface
        fields = ['full_name', 'phone', 'user_name', 'payment_method']
        write_only_fields = ['payment_method', 'phone']

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
        write_only_fields = ['phone',]

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
    
    def check_law_data_request(self, data, actual_law):
            current_incompetence = data.get('incompetence')
            current_specialization = data.get('specialization')
            self.check_actual_law(current_incompetence, actual_law)
            self.check_actual_law(current_specialization, actual_law)
            return True
            

    def check_actual_law (self, law_data:dict, actual_law:dict ):
        # надо как-то закешировать актуальные области права:
        for type_of_law in law_data:
            for law in law_data[type_of_law]:
                if law not in actual_law[type_of_law]:
                    raise serializers.ValidationError (f'{type_of_law}:{law} - вы указали недопустимую область права')      
        return True

   
    def create_law_profile(self, 
                           inst_interface:LawyerUserInterface, 
                           data):
        law_data=FieldsOfLaw.objects.all()
        used_values_law=[]
        for type_law in data['incompetence']:
            for area in data['incompetence'][type_law]:
                inst_interface.incompetence.add(law_data.get(area=area))
                used_values_law.append(area)
        for type_law in data['specialization']:
            for area in data['specialization'][type_law]:
                if area in used_values_law:
                    raise serializers.ValidationError('Error. Right fields in specialization and incompetence cannot be the same')              
                inst_interface.specialization.add(law_data.get(area=area))
        inst_interface.save()
        return inst_interface

    
    def check_user(self):
        current_user:User = self.validated_data['user_name']
        if current_user.kind_of_user==UsersKind.objects.get(pk=1):
            return False
        elif current_user.kind_of_user==None:
            current_user.kind_of_user=UsersKind.objects.get(pk=2)
            current_user.save()
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
        fields = ['username','email']
        read_only_fields = ['username']
        

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
    
    def check_fullname(self, data, user):
        if 'full_name' in data:
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
    def check_fullname(self, data, user):
        if 'full_name' in data:
            full_name:str = self.validated_data['full_name']
            first_name, last_name = full_name.split(' ')[0], full_name.split(' ')[1]
            user.first_name = first_name
            user.last_name = last_name
            user.save()
    
    def check_law_data_request(self, lawyer, data, actual_law):
        if 'incompetence' in data or 'specialization' in data:
            current_incompetence = data.get('incompetence', None)
            current_specialization = data.get('specialization', None)
            if current_incompetence is not None:
                self.check_actual_law(current_incompetence, actual_law)
            if current_specialization is not None:
                self.check_actual_law(current_specialization, actual_law)
            self.update_law_profile(lawyer, current_specialization, current_incompetence)

    def check_actual_law (self, law_data:dict, actual_law:dict ):
        # надо как-то закешировать актуальные области права:
        for type_of_law in law_data:
            for law in law_data[type_of_law]:
                if law not in actual_law[type_of_law]:
                    raise serializers.ValidationError (f'{law}: Вы указали недопустимую область права')      
        return True


    def update_law_profile(self, 
                           inst_interface:LawyerUserInterface, 
                           specialization_data=None,
                           incompetence_data=None):
        law_data=FieldsOfLaw.objects.all()
        used_values = []
        if incompetence_data is not None:
            inst_interface.incompetence.clear()
            for type_law in incompetence_data:
                for area in incompetence_data[type_law]:        
                    inst_interface.incompetence.add(law_data.get(area=area))
                    used_values.append(area)
        else:
            crud_used_values = inst_interface.incompetence.values_list("area")
            used_values = [value[0] for value in crud_used_values]
        if specialization_data is not None:
            inst_interface.specialization.clear()
            for type_law in specialization_data:
                for area in specialization_data[type_law]:        
                    if area not in used_values:
                        inst_interface.specialization.add(law_data.get(area=area))
                    else:
                        raise serializers.ValidationError(f'Error {area}. Right fields in specialization and incompetence cannot be the same')
                inst_interface.save()
                return inst_interface
        else:
            crud_specialization_data = inst_interface.specialization.values_list("area")
            specializations_list = [value[0] for value in crud_specialization_data]
            for value in used_values:
                   if value in  specializations_list:
                       raise serializers.ValidationError(f'Error {value}. Right fields in specialization and incompetence cannot be the same')
                   inst_interface.save()                       
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
    
    