from rest_framework import serializers
from legalApplication.models import LegalApp

class CreateLegalAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalApp
        fields = ['client', 'city', 'type_of_assistance', 'place_of_assistance',
                'note_of_application', 'type_of_law', 'specialization',
                 'authority', 'geolocation',]
        extra_kwargs = {
            'authority':{
                'required':False,
                'default': '',
            },
            'geolocation':{
                'required':False,
                'default': '',
            }
        }
    def save (self):
        new_legal_app = LegalApp(client = self.validated_data['client'],
                                city = self.validated_data['city'],
                                type_of_assistance = self.validated_data['type_of_assistance'],
                                place_of_assistance = self.validated_data['place_of_assistance'],
                                note_of_application = self.validated_data['note_of_application'],
                                type_of_law = self.validated_data['type_of_law'],
                                specialization = self.validated_data['specialization'],
                                authority = self.validated_data['authority'],
                                geolocation = self.validated_data['geolocation']
                                         )
        new_legal_app.clean()
        new_legal_app.save()
        return new_legal_app

class ReadLegalAppSerializer(serializers.ModelSerializer):
    class Meta():
        model = LegalApp
        exclude = ['type_of_law']
    
    
