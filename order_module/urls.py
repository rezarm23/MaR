from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('orders', views.OrderViewSet)
router.register('order-detail', views.OrderDetailViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
