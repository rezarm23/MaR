from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views


urlpatterns = [
    path('change-password', views.ChangePasswordAPIView.as_view()),
    path('user-profile', views.UserProfileAPIView.as_view()),
    path('register', views.RegisterAPIView.as_view()),
    path('activate/<str:activation_code>', views.ActivateUserAPIView.as_view()),
    path('login', views.LoginAPIView.as_view()),
    path('forget-password', views.ForgetPasswordAPIView.as_view()),
    path('forget-password/reset-password/<str:activation_code>', views.ResetPasswordAPIView.as_view()),
    path('me', views.user_info_view),
    path('logout', views.logout_view),

]
