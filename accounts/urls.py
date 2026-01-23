from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import SendCodeView, RegisterView, LoginView, PasswordResetConfirmView, PasswordResetRequestView, TelegrammLinkView

urlpatterns = [
    path('api/auth/send-code/', SendCodeView.as_view(), name='send_code'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', LoginView.as_view(), name='login'),

    path('api/auth/send_reset_password_code/', PasswordResetRequestView.as_view(), name='send_confirmation_change_password_code'),
    path('api/auth/confirm_change_password/', PasswordResetConfirmView.as_view(), name='confirm_chage_password'),
    
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/telegramm-link/', TelegrammLinkView.as_view(), name='telegramm_link'),
]
