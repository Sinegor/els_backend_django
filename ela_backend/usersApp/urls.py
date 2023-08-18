from django.urls import path, include
from usersApp.views import RegistrationView, LoginView, LogoutView, ChangePasswordView, \
                           GetCurrentUserView, RegistrationClientView, \
                           RegistrationLawyerView, RegistrationConfirmEmailView, UpdateUserView,\
                           UpdateClientView, UpdateLawyerView, ReadUserView, ReadClientView, ReadLawyerView,\
                           DeleteUserView, TestingView
from rest_framework_simplejwt import views as jwt_views




urlpatterns = [
    path('registration/client', RegistrationClientView.as_view(), name= 'client_register'),
    path('registration/lawyer', RegistrationLawyerView.as_view(), name='lawyer_register'),
    path('registration/starting/<str:user>', RegistrationConfirmEmailView.as_view()),
    path('registration', RegistrationView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('change-password', ChangePasswordView.as_view(), name='change pass'),
    path('token-refresh', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path ('current_user',GetCurrentUserView.as_view()),
    path('update/user', UpdateUserView.as_view()), 
    path('update/client', UpdateClientView.as_view()),
    path('update/lawyer', UpdateLawyerView.as_view()),
    path('read/user', ReadUserView.as_view()),
    path('read/client', ReadClientView.as_view()),
    path('read/lawyer', ReadLawyerView.as_view()),
    path ('delete/user', DeleteUserView.as_view()), 
    path ('testing', TestingView.as_view())

]
