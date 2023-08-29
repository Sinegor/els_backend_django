from django.contrib import admin
from django.contrib import admin

from legalApplication.models import LegalApp

# Register your models here.

class LegalAppAdmin(admin.ModelAdmin):
    list_display =('city', 'client', 'type_of_assistance', 'status', 'type_of_law',)
    fields = ('city', 'client', 'type_of_assistance', 'status', 'lawyer', 'type_of_law', 'specialization',
            'authority', 'geolocation' )

admin.site.register(LegalApp, LegalAppAdmin)