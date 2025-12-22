from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, QuickOrderView, CartValidateView, DeliveryChargeView, ManagerOrderListView, update_order_status

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('orders/quick-order/', QuickOrderView.as_view(), name='quick-order'),
    path('delivery-charges/', DeliveryChargeView.as_view(), name='delivery-charges'),
    path('cart/validate/', CartValidateView.as_view(), name='cart-validate'),
    path('manager-dashboard/', ManagerOrderListView.as_view(), name='manager-dashboard'),
    path('update-status/', update_order_status, name='update-order-status'),
    path('', include(router.urls)),
]
