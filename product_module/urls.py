from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('product-category', views.ProductCategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('grouped-products', views.GroupedProductListView.as_view()),
]
