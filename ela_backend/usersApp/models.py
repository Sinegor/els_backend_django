from django.db import models

from django.contrib.auth.models import AbstractUser

from django.contrib.auth.validators import UnicodeUsernameValidator
from location_field.forms.plain import PlainLocationField
#?:
#from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator

class UsersKind(models.Model):
    name = models.CharField(max_length=50)

class User (AbstractUser):
    kind_of_user = models.ForeignKey(UsersKind, on_delete=models.PROTECT, blank=True, null=True)
    


class ClientUserInterface(User):
    phoneNumberRegex = RegexValidator(regex = r"^\+?1?\d{8,15}$")
    name_of_interface = models.ForeignKey(UsersKind, on_delete=models.CASCADE, related_name='client_user_interface')
    user_id = models.OneToOneField(User,on_delete=models.CASCADE, related_name='client_user_interface')
    full_name = models.CharField (max_length=200, blank=False)
    email_confirm = models.BooleanField(unique=True, default=False)
    phone = models.CharField(max_length=16, unique=False, validators=[phoneNumberRegex])
    payment_method = models.CharField(max_length=200, default=None,) 
    current_requests = models.CharField(max_length=200, default=None)
    history_of_requests = models.CharField(max_length=200, default=None)
    
class LawyerUserInterface(User):
    phoneNumberRegex = RegexValidator(regex = r"^\+?1?\d{8,15}$")
    name_of_interface = models.ForeignKey(UsersKind, on_delete=models.CASCADE, related_name='lawer_user_interface')
    user_id = models.OneToOneField(User,on_delete=models.CASCADE, related_name='lawer_user_interface')
    full_name = models.CharField (max_length=200, blank=False)
    email_confirm = models.BooleanField(unique=True, default=False)
    phone = models.CharField(max_length=16, unique=False, validators=[phoneNumberRegex])
    payment_method = models.CharField(max_length=200, default=None,) 
    current_applications = models.CharField(max_length=200, default=None)
    history_of_applications = models.CharField(max_length=200, default=None)
    is_advokat = models.BooleanField(default=False)
    legal_education_check = models.BooleanField(default=False)
    preferred_location = models.TextField()
    specialization = models.TextField()
    incompetence = models.TextField()
    current_city = models.CharField(max_length=150)
    current_location =  PlainLocationField(based_fields=['current_city'], zoom=7)
    

    

