from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .views import SendCodeView, RegisterView, LoginView, PasswordResetConfirmView, PasswordResetRequestView, TelegrammLinkView, GetUserInfoView, UserUpdateView


class SwaggerTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(
        operation_description='Refresh access token using refresh token',
        tags=['Authentication'],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


urlpatterns = [
    path('auth/send-code/', SendCodeView.as_view(), name='send_code'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),

    path('auth/send_reset_password_code/', PasswordResetRequestView.as_view(), name='send_confirmation_change_password_code'),
    path('auth/confirm_change_password/', PasswordResetConfirmView.as_view(), name='confirm_chage_password'),
    
    path('auth/token/refresh/', SwaggerTokenRefreshView.as_view(), name='token_refresh'),
    path('auth/telegram-link/', TelegrammLinkView.as_view(), name='telegram_link'),
    path('auth/get_user/', GetUserInfoView.as_view(), name='get_user'),
    path('auth/user_update/', UserUpdateView.as_view(), name='user_update'),
]
