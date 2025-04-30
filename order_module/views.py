from rest_framework import viewsets

from order_module.models import OrderDetail, Order
from order_module.serializers import OrderDetailSerializer, OrderSerializer
from product_module.views import ProductPaginationViewSet


# Create your views here.
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = ProductPaginationViewSet

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailViewSet(viewsets.ModelViewSet):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    pagination_class = ProductPaginationViewSet

    def get_queryset(self):
        return OrderDetail.objects.filter(order__user=self.request.user)
