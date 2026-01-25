from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import VerificationCode

User = get_user_model()

class SendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()    
    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if user and user.is_active:
            raise serializers.ValidationError("User with this email already exists and is active.")
        return value

       

class RegisterSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=6, write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'password', 'code', 'first_name', 'last_name']

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')

        try:
            verification = VerificationCode.objects.get(email=email)
        except VerificationCode.DoesNotExist:
            raise serializers.ValidationError({"code": "Verification code not found. Please request a new one."})

        if verification.is_expired():
            raise serializers.ValidationError({"code": "Verification code has expired."})

        if verification.code != code:
            raise serializers.ValidationError({"code": "Invalid verification code."})

        return attrs

    def create(self, validated_data):
        validated_data.pop('code')  
        email = validated_data.get('email')
        User.objects.filter(email=email, is_active=False).delete()
        user = User.objects.create_user(**validated_data)
        user.is_active = True
        user.save()
        VerificationCode.objects.filter(email=email).delete()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(email=email, password=password)        
        if not user:
            existing_user = User.objects.filter(email=email).first()
            if existing_user and not existing_user.is_active:
                raise serializers.ValidationError({
                    "status": "not_verified",
                    "detail": "Please verify your email before logging in."
                })
            raise serializers.ValidationError("Invalid credentials.")

        if not user.is_active:
            raise serializers.ValidationError("This account is disabled.")
        attrs['user'] = user
        return attrs



class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('User with this email does not exists')
        return value

class ResetPasswordConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')
        
        try:
            verification = VerificationCode.objects.get(email=email, code=code)
            if verification.is_expired():
                raise serializers.ValidationError('Code was expired')
        except VerificationCode.DoesNotExist:
            raise serializers.ValidationError('Email or code is incorrect')
        return attrs



class GetUserInfoSerialzer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'telegram_id', 'role')
        read_only_fields = ('id', 'email', 'role')
    

