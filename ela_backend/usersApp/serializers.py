from rest_framework import serializers
from usersApp.models import User, UsersKind
from django.db import models
# for phone number vflidation:
#from django.core.validators import RegexValidator

class RegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'kind_of_user', 'password', 'email']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        user = User(email=self.validated_data['email'], username = self.validated_data['username'])
        user.kind_of_user = self.validated_data['kind_of_user']
        password = self.validated_data['password']
        user.set_password(password)
        user.save()
        return user




class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={"input_type": "password"}, required=True)
    new_password = serializers.CharField(style={"input_type": "password"}, required=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError({'current_password': 'Does not match'})
        return value