from rest_framework import status, views, permissions
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from .models import VerificationCode, get_expiry_time
from .serializers import SendCodeSerializer, RegisterSerializer, LoginSerializer, ResetPasswordConfirmSerializer, ResetPasswordEmailSerializer
from .helpers import send_verification_email, send_welcome_message
import random
import secrets


User = get_user_model

def get_tokens_by_user(user):
    refresh = RefreshToken.for_user(user)    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }

class SendCodeView(views.APIView):
    permission_classes = [permissions.AllowAny]
    @swagger_auto_schema(
            request_body=SendCodeSerializer,
            operation_description='Send verification code to email',
            tags=['Authentication'],
            consumes=['multipart/form-data']
    )
    def post(self, request):
        serializer = SendCodeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = str(random.randint(100000, 999999))
            obj, created = VerificationCode.objects.update_or_create(
                email=email,
                defaults={'code': code}
            )
            if not created:
                obj.refresh_code()
                code = obj.code
            try:
                send_verification_email(email=email, code=code)
            except Exception as e:
                return Response({"error": "Failed to send email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"message": "Verification code sent successfully."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(views.APIView):
    permission_classes = [permissions.AllowAny]
    @swagger_auto_schema(
            request_body=RegisterSerializer,
            operation_description='Register user with email and password',
            tags=['Authentication'],
            consumes=['multipart/form-data']
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_by_user(user)
            try:
                first_name = request.data.get('first_name')
                last_name = request.data.get('last_name')
                email = request.data.get('email')
                full_name = f'{first_name} {last_name}'
                send_welcome_message(email=email, full_name=full_name)
            except Exception:
                pass
            return Response({
                "message": "User registered successful",
                **tokens
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
            request_body=LoginSerializer,
            operation_description='Login user with email and password',
            tags=['Authentication'],
            consumes=['multipart/form-data']
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            tokens = get_tokens_by_user(user)
            return Response({
                'message': 'Login successful',
                **tokens
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=ResetPasswordEmailSerializer,
        operation_description='Send password reset code to email',
        tags=['Authentication'],
        consumes=['multipart/form-data']
    )

    def post(self, request):
        serializer = ResetPasswordEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = str(random.randint(100000, 999999))
            VerificationCode.objects.update_or_create(
                email=email,
                defaults={'code': code, 'expires_at': get_expiry_time()}
            )

            send_mail(
                'Reset password',
                f'You code for reset your password is {code}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )

            return Response({'message': "Reser code sended successfuly"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=ResetPasswordConfirmSerializer,
        operation_description='Confirm password reset with code',
        tags=['Authentication'],
        consumes=['multipart/form-data']
    )
    def post(self, request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            new_password = serializer.validated_data['new_password']            
            user = User.objects.get(email=email)
            user.set_password(new_password) 
            user.save()
            VerificationCode.objects.filter(email=email).delete()            
            return Response({"message": "Password changed successfuly."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TelegrammLinkView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        operation_description='Get Telegram bot deep link for linking account',
        tags=['Authentication'],
        consumes=['multipart/form-data']
    )

    def get(self, request):
        user = request.user
        token = secrets.token_urlsafe(16)
        user.telegram_token = token
        user.save()
        bot_username = settings.BOT_USERNAME
        deep_link = f"https://t.me/{bot_username}?start={token}"
        return Response({'link': deep_link}, status=status.HTTP_200_OK)






