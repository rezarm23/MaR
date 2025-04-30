import re
from datetime import timedelta
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from utils.utils import validate_password_strength, validate_unique_field, validate_login_field, send_activation_email
from .models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number']

    def validate_email(self, value):
        user = self.instance
        if value != user.email:
            if User.objects.filter(email=value).exclude(id=user.id).exists():
                raise serializers.ValidationError("این ایمیل قبلاً ثبت شده.")
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", value):
            raise serializers.ValidationError("فرمت ایمیل معتبر نیست.")
        return value

    def validate_username(self, value):
        user = self.instance
        if value != user.username:
            if User.objects.filter(username=value).exclude(id=user.id).exists():
                raise serializers.ValidationError("این نام کاربری قبلاً استفاده شده.")
        return value

    def validate_phone_number(self, value):
        user = self.instance
        if value != user.phone_number:
            if User.objects.filter(phone_number=value).exclude(id=user.id).exists():
                raise serializers.ValidationError("این شماره تلفن قبلاً ثبت شده.")
        if not re.fullmatch(r"^09\d{9}$", str(value)):
            raise serializers.ValidationError("شماره باید 11 رقمی و با 09 شروع شود.")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("رمز عبور باید حداقل ۸ کاراکتر باشد.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("باید حداقل یک عدد داشته باشد.")
        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError("باید حداقل یک حرف داشته باشد.")
        return value

    def save(self):
        user = self.context['user']
        old_password = self.initial_data['old_password']
        new_password = self.initial_data['new_password']

        if not user.check_password(old_password):
            raise serializers.ValidationError("رمز عبور قدیمی اشتباه است.")

        if user.check_password(new_password):
            raise serializers.ValidationError("رمز عبور جدید نمی‌تواند با رمز عبور قدیمی یکسان باشد.")

        user.set_password(new_password)
        user.save()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password']

    def validate(self, data):
        errors = {}
        email = data.get('email')
        phone_number = data.get('phone_number')
        username = data.get('username')
        password = data.get('password')

        if email:
            if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
                errors['email'] = "فرمت ایمیل معتبر نیست."
            else:
                try:
                    validate_unique_field(User, "email", email)
                except ValidationError as e:
                    errors['email'] = str(e)

        if phone_number:
            if not re.fullmatch(r"^09\d{9}$", str(phone_number)):
                errors['phone_number'] = "شماره باید 11 رقمی و با 09 شروع شود."
            else:
                try:
                    validate_unique_field(User, "phone_number", phone_number)
                except ValidationError as e:
                    errors['phone_number'] = str(e)

        if username:
            try:
                validate_unique_field(User, "username", username)
            except ValidationError as e:
                errors['username'] = str(e)

        if password:
            try:
                validate_password_strength(password)
            except ValidationError as e:
                errors['password'] = str(e)

        if errors:
            raise serializers.ValidationError(errors)

        return data

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
            raise serializers.ValidationError("نام کاربری/ایمیل یا رمز عبور اشتباه است.")

        attrs['user'] = user
        return attrs


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        User = get_user_model()
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('کاربری با این ایمیل پیدا نشد.')
        return value


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError('رمز عبور و تکرار آن یکسان نیستند.')

        validate_password_strength(password)

        return attrs

    def save(self, **kwargs):
        User = get_user_model()
        activation_code = self.context.get('activation_code')
        try:
            user = User.objects.get(activation_code=activation_code)
        except User.DoesNotExist:
            raise serializers.ValidationError('کد فعال‌سازی معتبر نیست.')

        if user.activation_code_expiration and timezone.now() > user.activation_code_expiration:
            return Response({"detail": "کد فعالسازی منقضی شده است."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(self.validated_data['password'])
        user.activation_code = None
        user.activation_code_expiration = None
        user.save()

        return user


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']