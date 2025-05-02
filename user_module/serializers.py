import re
from datetime import timedelta
from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from utils.util.util import validate_password_strength, validate_unique_field, send_activation_email
from .models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number']

    def validate_email(self, value):
        user = self.instance
        if value != user.email:
            if User.objects.filter(email=value).exclude(id=user.id).exists():
                raise serializers.ValidationError("This email has already been registered.")
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", value):
            raise serializers.ValidationError("The email format is not valid.")
        return value

    def validate_username(self, value):
        user = self.instance
        if value != user.username:
            if User.objects.filter(username=value).exclude(id=user.id).exists():
                raise serializers.ValidationError("This username has already been used.")
        return value

    def validate_phone_number(self, value):
        user = self.instance
        if value != user.phone_number:
            if User.objects.filter(phone_number=value).exclude(id=user.id).exists():
                raise serializers.ValidationError("This phone number is already registered.")
        if not re.fullmatch(r"^09\d{9}$", str(value)):
            raise serializers.ValidationError("The number must be 11 digits and start with 09.")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("The password must be at least 8 characters long.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("It must have at least one number.")
        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError("It must have at least one letter.")
        return value

    def save(self):
        user = self.context['user']
        old_password = self.initial_data['old_password']
        new_password = self.initial_data['new_password']

        if not user.check_password(old_password):
            raise serializers.ValidationError("The old password is incorrect.")

        if user.check_password(new_password):
            raise serializers.ValidationError("The new password cannot be the same as the old password.")

        user.set_password(new_password)
        user.save()


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    phone_number = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password']

    def validate_email(self, value):
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", value):
            raise serializers.ValidationError("The email format is not valid.")
        if not value:
            raise serializers.ValidationError("Email must be entered.")
        return validate_unique_field(User, "email", value)

    def validate_phone_number(self, value):
        if not re.fullmatch(r"^09\d{9}$", str(value)):
            raise serializers.ValidationError("The number must be 11 digits and start with 09.")
        if not value:
            raise serializers.ValidationError("A phone number must be entered.")
        return validate_unique_field(User, "phone_number", value)

    def validate_username(self, value):
        if not value:
            raise serializers.ValidationError("Username must be entered.")
        return validate_unique_field(User, "username", value)

    def validate_password(self, value):
        try:
            return validate_password_strength(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.is_active = False
        user.activation_code = get_random_string(length=72)
        user.activation_code_expiration = timezone.now() + timedelta(hours=24)
        user.save()
        send_activation_email(user)
        return user


class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username_or_email = attrs.get('username_or_email')
        password = attrs.get('password')

        user = authenticate(username=username_or_email, password=password)
        if user is None:
            User = get_user_model()
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        if not user:
            raise serializers.ValidationError("The username/email or password is incorrect.")

        attrs['user'] = user
        return attrs


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        User = get_user_model()
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('No user with this email was found.')
        return value


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError('The password and its repetition are not the same.')

        validate_password_strength(password)

        return attrs

    def save(self, **kwargs):
        User = get_user_model()
        activation_code = self.context.get('activation_code')
        try:
            user = User.objects.get(activation_code=activation_code)
        except User.DoesNotExist:
            raise serializers.ValidationError('The activation code is not valid.')

        if user.activation_code_expiration and timezone.now() > user.activation_code_expiration:
            return Response({"detail": "The activation code has expired."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(self.validated_data['password'])
        user.activation_code = None
        user.activation_code_expiration = None
        user.save()

        return user


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
