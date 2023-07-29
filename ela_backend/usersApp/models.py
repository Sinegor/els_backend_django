from django.db import models

from django.contrib.auth.models import AbstractUser

from django.contrib.auth.validators import UnicodeUsernameValidator
from location_field.forms.plain import PlainLocationField
#?:
#from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator

class UsersKind(models.Model):
    name = models.CharField(max_length=50, verbose_name='Kind of user', unique=True)
    def __str__(self):
        return (self.name)
    
    class Meta:
        verbose_name = "Вид пользователя"
        verbose_name_plural = 'Разновидности пользоватлей'

    

class User (AbstractUser):
    kind_of_user = models.ForeignKey(UsersKind, 
                                     blank=True, 
                                     null=True, 
                                     on_delete=models.PROTECT, verbose_name= 'тип пользователя',
                                     )
    def __str__(self):
        return(self.username)
    


class ClientUserInterface(models.Model):
    class Meta:
        verbose_name = "Пользователь-клиент"
        verbose_name_plural = 'Пользователи-клиенты'
    
    def get_default_type_user():
        return UsersKind.objects.get(id=1)
    
    phoneNumberRegex = RegexValidator(regex = r"^\+?1?\d{8,15}$")
    name_of_interface = models.ForeignKey(UsersKind,  
                                          on_delete=models.CASCADE, 
                                          related_name='client_user_interface',
                                          default= get_default_type_user,
                                          verbose_name='тип пользователя',
                                          )
    user_name = models.OneToOneField(User,on_delete=models.CASCADE, 
                                        related_name='client_user_interface', 
                                        verbose_name='пользователь',
                                        to_field='username'
                                       )
    full_name = models.CharField (max_length=200, blank=False)
    email_confirm = models.BooleanField(default=False)
    phone = models.CharField(max_length=16, validators=[phoneNumberRegex])
    payment_method = models.CharField(max_length=200, blank=True,) 
    current_requests = models.CharField(max_length=200, blank=True)
    history_of_requests = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return (f"{self.user_name}: {self.full_name}")

    
class LawyerUserInterface(models.Model):
    def get_default_type_user():
        return UsersKind.objects.get(id=2)
    phoneNumberRegex = RegexValidator(regex = r"^\+?1?\d{8,15}$")
    name_of_interface = models.ForeignKey(UsersKind, default=get_default_type_user,
                                          on_delete=models.CASCADE, 
                                          related_name='lawer_user_interface',
                                          verbose_name='тип пользователя'
                                          )
    user_name = models.OneToOneField(User,on_delete=models.CASCADE, 
                                   related_name='lawer_user_interface',
                                   verbose_name='пользователь',
                                   to_field= 'username' 
                                   )
    full_name = models.CharField (max_length=200, blank=False)
    email_confirm = models.BooleanField(default=False)
    phone = models.CharField(max_length=16, validators=[phoneNumberRegex])
    payment_method = models.CharField(max_length=200, blank=True, default=None,) 
    current_applications = models.CharField(max_length=200, blank=True, default=None)
    history_of_applications = models.CharField(max_length=200, blank=True, default=None)
    is_advokat = models.BooleanField(default=False)
    legal_education_check = models.BooleanField(default=False)
    preferred_location = models.TextField()
    specialization = models.TextField()
    incompetence = models.TextField()
    current_city = models.CharField(max_length=150)
    current_location =  PlainLocationField(based_fields=['current_city'], zoom=7)
    
    def __str__(self):
        return (f"{self.user_id}: {self.full_name}")

    

