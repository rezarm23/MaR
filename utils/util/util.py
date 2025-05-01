import re
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


def validate_password_strength(password):
    if len(password) < 8:
        raise ValidationError('رمز عبور باید حداقل ۸ کاراکتر باشد.')

    if not re.search(r'[A-Z]', password):
        raise ValidationError('رمز عبور باید حداقل یک حرف بزرگ داشته باشد.')

    if not re.search(r'[a-z]', password):
        raise ValidationError('رمز عبور باید حداقل یک حرف کوچک داشته باشد.')

    if not re.search(r'[0-9]', password):
        raise ValidationError('رمز عبور باید حداقل یک عدد داشته باشد.')

    return password


def validate_unique_field(model, field_name, value):
    if model.objects.filter(**{field_name: value}).exists():
        raise serializers.ValidationError(f"این {field_name} قبلاً ثبت شده.")
    return value


def validate_login_field(model, field_name, value):
    if not model.objects.filter(**{field_name: value}).exists():
        raise serializers.ValidationError(f" {field_name} وارد شده وجود ندارد.")
    return value


def send_activation_email(user):
    activation_link = f"http://localhost:3000/user/activate/{user.activation_code}/"
    subject = "فعالسازی حساب کاربری"
    message = f"برای فعالسازی حساب خود روی لینک زیر کلیک کنید:\n{activation_link}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def send_reset_password_email(user):
    activation_link = f"http://localhost:3000/user/reset-pass/{user.activation_code}/"
    subject = "تغییر رمز عبور حساب کاربری"
    message = f"برای تغییر رمز عبور حساب خود روی لینک زیر کلیک کنید:\n{activation_link}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


