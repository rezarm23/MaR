import re
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


def validate_password_strength(password):
    if len(password) < 8:
        raise ValidationError('The password must be at least 8 characters long.')

    if not re.search(r'[A-Z]', password):
        raise ValidationError('The password must contain at least one uppercase letter.')

    if not re.search(r'[a-z]', password):
        raise ValidationError('The password must contain at least one lowercase letter.')

    if not re.search(r'[0-9]', password):
        raise ValidationError('The password must contain at least one number.')

    return password


def validate_unique_field(model, field_name, value):
    if model.objects.filter(**{field_name: value}).exists():
        raise serializers.ValidationError(f"This {field_name} is already registered.")
    return value


def validate_login_field(model, field_name, value):
    if not model.objects.filter(**{field_name: value}).exists():
        raise serializers.ValidationError(f"The entered {field_name} does not exist.")
    return value


def send_activation_email(user):
    activation_link = f"http://mar-9oop.onrender.com/user/activate/{user.activation_code}/"
    subject = "Account activation"
    message = f"Click on the link below to activate your account:\n{activation_link}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def send_reset_password_email(user):
    activation_link = f"http://mar-9oop.onrender.com/user/reset-pass/{user.activation_code}/"
    subject = "Change account password"
    message = f"Click on the link below to change your account password:\n{activation_link}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


