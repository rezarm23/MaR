from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework import generics
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from utils.util.util import send_reset_password_email
from .models import User
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChangePasswordSerializer, RegisterSerializer, LoginSerializer, UserProfileSerializer, \
    ForgetPasswordSerializer, ResetPasswordSerializer, UserInfoSerializer


# Create your views here.


class UserProfileAPIView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordAPIView(APIView):
    class ChangePasswordAPIView(APIView):
        permission_classes = [IsAuthenticated]

        def post(self, request):
            serializer = ChangePasswordSerializer(
                data=request.data,
                context={'user': request.user}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"success": 1, "message": "رمز عبور با موفقیت تغییر کرد."}, status.HTTP_200_OK)


class RegisterAPIView(APIView):
    # permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'ثبت نام موفق بود. لطفاً ایمیل خود را برای ادامه روند ثبت نام و فعال‌سازی حساب چک کنید.',
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'phone_number': user.phone_number,
                    'activation_code': user.activation_code
                }
            }, status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateUserAPIView(APIView):
    def get(self, request, activation_code):
        try:
            user = User.objects.get(activation_code=activation_code)
        except User.DoesNotExist:
            return Response({"detail": "کد فعالسازی معتبر نیست."}, status=status.HTTP_400_BAD_REQUEST)

        if user.activation_code_expiration and timezone.now() > user.activation_code_expiration:
            return Response({"detail": "کد فعالسازی منقضی شده است."}, status=status.HTTP_400_BAD_REQUEST)

        if user.is_active:
            return Response({"detail": "حساب کاربری قبلاً فعال شده است."}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.activation_code = None
        user.activation_code_expiration = None
        user.save()

        return Response({"success": 1, "detail": "حساب کاربری با موفقیت فعال شد."}, status=status.HTTP_200_OK)


class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({"success": 1,
                         'refresh': str(refresh),
                         'access': str(refresh.access_token),
                         }, status=status.HTTP_200_OK)


class ForgetPasswordAPIView(APIView):
    def post(self, request):
        serializer = ForgetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        User = get_user_model()
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)

        user.activation_code = get_random_string(length=72)
        user.activation_code_expiration = timezone.now() + timedelta(hours=24)
        user.save()
        send_reset_password_email(user)

        return Response({"success": 1,
                         'detail': 'ایمیل بازیابی رمز عبور ارسال شد.',
                         'activation_code': user.activation_code
                         }, status=status.HTTP_200_OK)


class ResetPasswordAPIView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request, activation_code):
        User = get_user_model()
        try:
            user = User.objects.get(activation_code=activation_code)
        except User.DoesNotExist:
            return Response({'error': 'کد فعال‌سازی معتبر نیست.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data, context={'activation_code': activation_code})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"success": 1, 'detail': 'رمز عبور با موفقیت تغییر کرد.'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info_view(request):
    serializer = UserInfoSerializer(request.user)
    return Response(serializer.data)
