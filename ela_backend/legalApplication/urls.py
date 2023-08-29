from django.urls import path, include
from legalApplication.views import CreateLegalAppView

urlpatterns = [
    path('create', CreateLegalAppView.as_view())
]