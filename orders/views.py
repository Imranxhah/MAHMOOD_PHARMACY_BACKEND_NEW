from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem, DeliveryCharge
from .serializers import OrderSerializer, CreateOrderSerializer
from products.models import Product
from django.shortcuts import render
from django.db.models import Sum, Count, Q, Case, When, Value, IntegerField
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView
from django.http import JsonResponse
from django.views.decorators.http import require_POST

class ManagerOrderListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Order
    template_name = 'orders/manager_dashboard.html'
    context_object_name = 'orders'
    paginate_by = 20

    login_url = '/admin/login/' # Ensure redirect goes to admin login

    def test_func(self):
        user = self.request.user
        # Debugging permissions
        print(f"DASHBOARD ACCESS CHECK: User={user.email}, is_staff={user.is_staff}, is_superuser={user.is_superuser}, branch={user.branch}")
        
        # Superusers always allowed
        if user.is_superuser:
            return True
            
        # Staff must have a branch
        if user.is_staff and user.branch:
            return True
            
        return False

    def get_queryset(self):
        # Start with all orders
        queryset = Order.objects.all()
        
        # 1. Annotate for custom sorting
        # Rule: Pending(1) -> Shipped(2) -> Delivered(3) -> Others(4)
        queryset = queryset.annotate(
            status_priority=Case(
                When(status='Pending', then=Value(1)),
                When(status='Processing', then=Value(1)), # Treat processing same as pending or slightly after? Let's say 1 for now or 2
                When(status='Shipped', then=Value(2)),
                When(status='Delivered', then=Value(3)),
                When(status='Cancelled', then=Value(4)),
                default=Value(5),
                output_field=IntegerField(),
            )
        )
        
        # 2. Sort: Priority Ascending, then Created At Ascending (Oldest First)
        queryset = queryset.order_by('status_priority', 'created_at')

        user = self.request.user
        
        # Filter by branch if not superuser
        if not user.is_superuser and user.branch:
            queryset = queryset.filter(branch=user.branch)
            
        # Optional Filters from GET params
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Stats logic
        qs = self.get_queryset() 
        # Note: For stats, we usually want totals regardless of pagination, 
        # but maybe we should use the base filtered QS (by branch) without the search filters?
        # Let's stick to branch-wide stats.
        
        base_qs = Order.objects.all()
        if not self.request.user.is_superuser and self.request.user.branch:
            base_qs = base_qs.filter(branch=self.request.user.branch)

        context['total_orders'] = base_qs.count()
        context['pending_orders'] = base_qs.filter(status='Pending').count()
        context['completed_orders'] = base_qs.filter(status='Delivered').count()
        context['total_revenue'] = base_qs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        context['branch_name'] = self.request.user.branch.name if self.request.user.branch else "All Branches"
        
        return context

@require_POST
def update_order_status(request):
    import json
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        new_status = data.get('status')
        
        order = get_object_or_404(Order, id=order_id)
        
        # Permission check: User must be superuser OR manager of the order's branch
        if not request.user.is_authenticated:
             return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
             
        if not request.user.is_superuser:
            if order.branch != request.user.branch:
                 return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
        
        order.status = new_status
        order.save()
        
        return JsonResponse({'success': True, 'message': 'Status updated'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().order_by('-created_at')
        return Order.objects.filter(user=user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data)
        if serializer.is_valid():
            items_data = serializer.validated_data['items']
            shipping_address = serializer.validated_data['shipping_address']
            contact_number = serializer.validated_data['contact_number']

            # Validate Stock First
            product_ids = [item['product_id'] for item in items_data]
            products = Product.objects.filter(id__in=product_ids)
            product_map = {str(p.id): p for p in products}

            if len(products) != len(set(product_ids)):
                 return Response({"error": "One or more products found invalid."}, status=status.HTTP_400_BAD_REQUEST)

            total_amount = 0
            order_items_to_create = []

            try:
                with transaction.atomic():
                    branch_id = serializer.validated_data.get('branch_id')
                    payment_method = serializer.validated_data.get('payment_method', 'COD')
                    order_type = serializer.validated_data.get('order_type', 'Normal')

                    # Create Order Header
                    order = Order.objects.create(
                        user=request.user,
                        shipping_address=shipping_address,
                        contact_number=contact_number,
                        branch_id=branch_id,
                        payment_method=payment_method,
                        order_type=order_type,
                        total_amount=0 # Update later
                    )

                    for item in items_data:
                        pid = str(item['product_id'])
                        quantity = int(item['quantity'])
                        product = product_map.get(pid)

                        if not product:
                             raise Exception(f"Product {pid} not found")

                        if product.stock < quantity:
                            raise Exception(f"Insufficient stock for {product.name}. Available: {product.stock}")

                        # Deduct Stock
                        product.stock -= quantity
                        product.save()

                        price = product.price
                        total_amount += price * quantity

                        order_items_to_create.append(OrderItem(
                            order=order,
                            product=product,
                            quantity=quantity,
                            price_at_purchase=price
                        ))

                    # Bulk Create Items
                    OrderItem.objects.bulk_create(order_items_to_create)

                    # Update Total
                    order.total_amount = total_amount
                    order.save()

                    # Serialize Response
                    response_serializer = OrderSerializer(order)
                    return Response(response_serializer.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        # Only admin allows status update
        if not request.user.is_staff:
             return Response({"error": "Only admins can update order status."}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def cancel_order(self, request, pk=None):
        order = self.get_object()
        
        if order.status != 'Pending':
             return Response({"error": "Cannot cancel order that is not pending."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # Restore Stock
                for item in order.items.all():
                    product = item.product
                    product.stock += item.quantity
                    product.save()
                
                order.status = 'Cancelled'
                order.save()
                return Response({"message": "Order cancelled successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuickOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Implementation of a simplified "Re-order" or "Quick Order"
        # For now, let's assume it accepts a single product_id and quantity for instant checkout
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        if not product_id:
             return Response({"error": "Product ID required."}, status=status.HTTP_400_BAD_REQUEST)
             
        # Reuse logic? For simplicity, let's just forward to the main logic via internal call or duplicate minimal logic
        # Duplicating minimal logic for speed
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
             return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        if product.stock < quantity:
             return Response({"error": f"Insufficient stock. Available: {product.stock}"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                product.stock -= quantity
                product.save()
                
                # Use user profile defaults if available, else require in body
                # For quick order, we assume user profile has phone/address or we take from request
                # Fallback to defaults
                shipping_address = request.data.get('shipping_address', 'Default Address') 
                contact_number = request.data.get('contact_number', request.user.mobile)
                
                order = Order.objects.create(
                    user=request.user,
                    shipping_address=shipping_address,
                    contact_number=contact_number,
                    order_type='Quick',
                    total_amount=product.price * quantity
                )
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price_at_purchase=product.price
                )
                
                return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CartValidateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        items = request.data.get('items', []) # [{"product_id": 1, "quantity": 1}]
        errors = []
        
        for item in items:
            pid = item.get('product_id')
            qty = item.get('quantity', 1)
            try:
                product = Product.objects.get(id=pid)
                if product.stock < qty:
                    errors.append(f"{product.name}: Only {product.stock} left.")
            except Product.DoesNotExist:
                errors.append(f"Product ID {pid} not found.")
                
        if errors:
            return Response({"valid": False, "errors": errors}, status=status.HTTP_200_OK) # Return 200 with valid:False logic
        
        return Response({"valid": True}, status=status.HTTP_200_OK)

class DeliveryChargeView(APIView):
    permission_classes = [] # Allow Any (Public)

    def get(self, request):
        # Return the first delivery charge object, or 0 if none
        charge = DeliveryCharge.objects.first()
        if charge:
            return Response({"amount": charge.amount}, status=status.HTTP_200_OK)
        return Response({"amount": 0.00}, status=status.HTTP_200_OK)
