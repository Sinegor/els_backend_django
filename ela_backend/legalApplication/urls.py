from django.urls import path, include
from legalApplication.views import CreateLegalAppView, ReadLegalAppView

urlpatterns = [
    path('create', CreateLegalAppView.as_view()),
    path('read', ReadLegalAppView.as_view()) 
]