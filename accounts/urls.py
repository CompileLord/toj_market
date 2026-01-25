from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .views import SendCodeView, RegisterView, LoginView, PasswordResetConfirmView, PasswordResetRequestView, TelegrammLinkView, GetUserInfoView


class SwaggerTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(
        operation_description='Refresh access token using refresh token',
        tags=['Authentication'],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


urlpatterns = [
    path('api/auth/send-code/', SendCodeView.as_view(), name='send_code'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', LoginView.as_view(), name='login'),

    path('api/auth/send_reset_password_code/', PasswordResetRequestView.as_view(), name='send_confirmation_change_password_code'),
    path('api/auth/confirm_change_password/', PasswordResetConfirmView.as_view(), name='confirm_chage_password'),
    
    path('api/auth/token/refresh/', SwaggerTokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/telegramm-link/', TelegrammLinkView.as_view(), name='telegramm_link'),
    path('api/auth/get-user-info/', GetUserInfoView.as_view(), name='get_user_info'),
]
