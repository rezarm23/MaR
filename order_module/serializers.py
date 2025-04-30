from rest_framework import serializers
from order_module.models import Order, OrderDetail


class OrderSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'is_paid', 'payment_date', 'total_price']

    def get_total_price(self, obj):
        return obj.total_price


class OrderDetailSerializer(serializers.ModelSerializer):
    total_item_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderDetail
        fields = '__all__'

    def get_total_item_price(self, obj):
        return (obj.final_price or 0) * obj.quantity
