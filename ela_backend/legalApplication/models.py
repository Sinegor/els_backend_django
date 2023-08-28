from django.db import models
from django.core.exceptions import ValidationError
from usersApp.models import User, FieldsOfLaw, ClientUserInterface, LawyerUserInterface

class LawType(models.Model):
    name = models.CharField(
                            max_length=50,
                            verbose_name='отрасль права',
                            unique=True
                            )
    def __str__(self) -> str:
        return self.name
    class Meta:
        verbose_name = 'раздел права'
        verbose_name_plural = 'разделы права'

class LegalApp(models.Model):
        
    class Meta:
        verbose_name = 'Заявка на юридическую помощь'
        verbose_name_plural = 'Заявки на скорую юридическую помощь'
        ordering = ['client']

    CONSULTATION = 'need consultation'
    PARTICIPATION = 'need participation'
    DOCUMENTS = 'need docs'
    ANOTHER = 'another'
    
    L_PLACE = 'place of lawyer'
    C_PLACE = 'place of client'

    A_ACCEPTED = 'application is accepted'
    A_SEARCH = 'search for a lawyer'
    A_ON_WAY = 'on the way'
    A_PROVIDED = 'assistance is provided'
    A_COMPLETED = 'assistance completed'
    A_DISPUT = 'open dispute'
    A_END = 'application ended'

    
    ASSISTANCE = [
        (CONSULTATION, 'юридическая консультация'),
        (PARTICIPATION, 'участие в юридическом мероприятии'),
        (DOCUMENTS, 'составление юридических документов'),
        (ANOTHER, 'иное'),
    ]

    ASSISTANCE_PLACE = [
        (L_PLACE, 'помощь по месту нахождения юриста'),
        (C_PLACE, 'помомщь по месту нахождения клиента'),
    ]

    STATUS = [
        (A_ACCEPTED, 'заявка принята'),
        (A_SEARCH, 'осуществляется поиск юриста'),
        (A_ON_WAY, 'в дороге'),
        (A_PROVIDED, 'помощь оказывается'),
        (A_COMPLETED, 'оказание юридической помощи окончено'),
        (A_DISPUT, 'открыт диспут'),
        (A_END, 'заявка закрыта'),
    ]


    client = models.ForeignKey(
                               ClientUserInterface,
                               on_delete=models.CASCADE,
                               verbose_name='заказчик',
                               )
    
    type_of_assistance = models.CharField(
                                max_length= 50,
                                verbose_name= 'тип юридической помощи',
                                choices = ASSISTANCE
                                )
    place_of_assistance = models.CharField(
                                            max_length=50,
                                            verbose_name='место получения юридической помощи',
                                            choices=ASSISTANCE_PLACE,
                                            blank=True
    )

    note_of_application = models.TextField(verbose_name='пояснения клиента')

    type_of_law = models.ForeignKey(LawType, on_delete=models.SET_NULL,
                                    to_field='name', 
                                    verbose_name='область права',
                                    null=True)

    specialization = models.ForeignKey(FieldsOfLaw, on_delete=models.SET_NULL, 
                                       verbose_name='специализация',
                                       to_field= 'area',
                                       null=True
                                         )

    status = models.CharField (max_length=150, 
                               verbose_name= 'статус заявки',
                               choices=STATUS,
                               default= A_ACCEPTED
                               )
    
    authority = models.CharField(max_length=150,
                                verbose_name='орган власти, в котором необходимо представлять интересы клиента',
                                blank=True,
                                
                                )
    geolocation = models.CharField( max_length= 100,
                                   verbose_name='Координаты нахождения заказчика',
                                   blank= True,
                                
    )

    lawer = models.ForeignKey(LawyerUserInterface, 
                              on_delete=models.PROTECT,
                              blank=True,
                              default=True
                              )
    
    def clean(self):
        if self.type_of_assistance == self.PARTICIPATION and self.authority is '':
            raise ValidationError('If legal assistance is required in the form of representation before an authority, the authority must be identified')
        if self.place_of_assistance == self.C_PLACE and self.geolocation is '':
            raise ValidationError ('You must indicate where exactly the lawyer should arrive') 


# class CivilApplication(models.Model):
#     ...
    
    
# class CriminalApplication(models.Model):
#     ...

# class AdministrativeApplication(models.Model):
#     ...
    

