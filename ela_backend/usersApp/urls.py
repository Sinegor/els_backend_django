from django.urls import path, include
from usersApp.views import RegistrationView, LoginView, LogoutView, ChangePasswordView




urlpatterns = [
    path('registration', RegistrationView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('change-password', ChangePasswordView.as_view(), name='change pass'),
#    path('accounts/token-refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]