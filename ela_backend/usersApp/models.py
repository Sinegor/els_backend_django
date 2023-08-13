from django.db import models

from django.contrib.auth.models import AbstractUser

from django.contrib.auth.validators import UnicodeUsernameValidator
from location_field.forms.plain import PlainLocationField
#?:
#from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator

class UsersKind(models.Model):
    name = models.CharField(max_length=50, 
    verbose_name='Kind of user', 
                            unique=True)
    def __str__(self):
        return (self.name)
    
    class Meta:
        verbose_name = "Вид пользователя"
        verbose_name_plural = 'Разновидности пользователей'

    
class User (AbstractUser):
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Все пользователи'
        ordering = ['kind_of_user', 'username']

    def __str__(self):
        return(self.username)
    
    kind_of_user = models.ForeignKey(UsersKind, 
                                     blank=True, 
                                     null=True, 
                                     on_delete=models.PROTECT, 
                                     verbose_name= 'тип пользователя',
                                     )
    email_confirm = models.BooleanField(default=False)
    

class ClientUserInterface(models.Model):
    class Meta:
        verbose_name = "Пользователь-клиент"
        verbose_name_plural = 'Пользователи-клиенты'
        ordering = ['user_name', 'full_name']
    
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
    phone = models.CharField(max_length=16, validators=[phoneNumberRegex])
    payment_method = models.CharField(max_length=200, blank=True,) 
    current_requests = models.CharField(max_length=200, blank=True,
                                        verbose_name='Текущие запросы на помощь')
    history_of_requests = models.CharField(max_length=200, blank=True, verbose_name='История запросов')
    
    def __str__(self):
        return (f"{self.user_name}: {self.full_name}")

class FieldsOfLaw (models.Model):
    class Meta:
        verbose_name = "Отрасль"
        verbose_name_plural = 'Отрасли права'
        ordering = ['type', 'area']
    area = models.CharField(max_length=70, blank=False, verbose_name='сфера отношений', unique=True)
    type = models.CharField(max_length=25, blank=False, verbose_name='область права')
    def __str__(self):
        return self.area

# class Specialization (models.Model):
#     lawyer = models.ForeignKey('LawyerUserInterface', on_delete=models.CASCADE, to_field='username')
#     area_law = models.ForeignKey(FieldsOfLaw, on_delete=models.CASCADE, to_field='area')

# class incompetence (models.Model):
#     lawyer = models.ForeignKey('LawyerUserInterface', on_delete=models.CASCADE, to_field='username')
#     area_law = models.ForeignKey(FieldsOfLaw, on_delete=models.CASCADE, to_field='area')

class LawyerUserInterface(models.Model):

    class Meta:
            verbose_name = "Пользователь-юрист"
            verbose_name_plural = 'Пользователи-юристы'
            ordering = ['is_advokat', 'user_name', 'full_name']
    
    def get_default_type_user():
        return UsersKind.objects.get(id=2)
    
    def __str__(self):
        return (f"{self.user_name}: {self.name_of_interface}")

    phoneNumberRegex = RegexValidator(regex = r"^\+?1?\d{8,15}$")
    name_of_interface = models.ForeignKey(UsersKind, 
                                          default=get_default_type_user,
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
    phone = models.CharField(max_length=16, validators=[phoneNumberRegex])
    payment_method = models.CharField(max_length=200, blank=True, ) 
    current_applications = models.CharField(max_length=200, blank=True,
                                            verbose_name="Текущие заказы")
    history_of_applications = models.CharField(max_length=200, blank=True,
                                               verbose_name='История заказов')
    is_advokat = models.BooleanField(default=False)
    legal_education_check = models.BooleanField(default=False)
    preferred_location = models.CharField(max_length=150)
    specialization = models.ManyToManyField(FieldsOfLaw, related_name='lawyer_specialization', db_table='lawyersSpecialization' )
    incompetence = models.ManyToManyField(FieldsOfLaw, db_table='lawyersIncompetence' )
    current_city = models.CharField(max_length=150)
    current_location =  PlainLocationField(based_fields=['current_city'], zoom=7, blank = True)

    
    




