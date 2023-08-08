from django.urls import path, include
from usersApp.views import RegistrationView, LoginView, LogoutView, ChangePasswordView, \
                           GetCurrentUser, RegistrationClientView, \
                           RegistrationLawyerView, RegistrationConfirmEmail
from rest_framework_simplejwt import views as jwt_views




urlpatterns = [
    path('registration/client', RegistrationClientView.as_view(), name= 'client_register'),
    path('registration/lawyer', RegistrationLawyerView.as_view(), name='lawyer_register'),
    path('registration/starting/<str:user>', RegistrationConfirmEmail.as_view()),
    path('registration', RegistrationView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('change-password', ChangePasswordView.as_view(), name='change pass'),
    path('token-refresh', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path ('current_user',GetCurrentUser.as_view()),
]
