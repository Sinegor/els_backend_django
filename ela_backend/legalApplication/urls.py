from django.urls import path, include
from legalApplication.views import CreateLegalApp

urlpatterns = [
    path('create', CreateLegalApp.as_view())
]