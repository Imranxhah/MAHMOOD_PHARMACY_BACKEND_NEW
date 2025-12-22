from rest_framework import viewsets, generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser
from django.db.models import Q, Count
import pandas as pd
from .models import Category, Product, Favorite
from .serializers import (
    CategorySerializer, 
    ProductSerializer, 
    FavoriteSerializer, 
    ProductBulkUploadSerializer
)

class HomeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # 1. All Categories (for the top list)
        all_categories = Category.objects.all()
        
        # 2. Hot Categories Sections (ordered by order count)
        hot_categories = Category.objects.annotate(
            popularity=Count('products__order_items')
        ).order_by('-popularity')

        sections = []
        for category in hot_categories:
            # Get top 10 products for this category
            products = Product.objects.filter(category=category, is_active=True)[:10]
            if products.exists():
                sections.append({
                    "category": CategorySerializer(category).data,
                    "products": ProductSerializer(products, many=True, context={'request': request}).data
                })

        return Response({
            "categories": CategorySerializer(all_categories, many=True).data,
            "sections": sections
        })

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'category__name']
    ordering_fields = ['price', 'created_at', 'stock']
    ordering = ['-created_at'] # Default ordering

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'bulk_upload']:
            return [IsAdminUser()]
        return [AllowAny()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
            
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        return queryset

class ProductBulkUploadView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser]

    def post(self, request):
        serializer = ProductBulkUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            try:
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                elif file.name.endswith('.xlsx'):
                    df = pd.read_excel(file)
                else:
                    return Response({"error": "Invalid file format. Only CSV or Excel allowed."}, status=status.HTTP_400_BAD_REQUEST)

                # Expect columns: name, category, price, stock, description
                created_count = 0
                updated_count = 0
                errors = []

                for index, row in df.iterrows():
                    try:
                        category_name = row.get('category')
                        category, _ = Category.objects.get_or_create(name=category_name)
                        
                        product, created = Product.objects.update_or_create(
                            name=row.get('name'),
                            defaults={
                                'category': category,
                                'price': row.get('price'),
                                'stock': row.get('stock'),
                                'description': row.get('description', ''),
                                'is_active': True
                            }
                        )
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1
                            
                    except Exception as e:
                        errors.append(f"Row {index}: {str(e)}")

                return Response({
                    "message": "Bulk upload processed.",
                    "created": created_count,
                    "updated": updated_count,
                    "errors": errors
                }, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FavoriteListView(generics.ListAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

class FavoriteToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({"error": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)

        if not created:
            favorite.delete()
            return Response({"message": "Removed from favorites.", "is_favorite": False}, status=status.HTTP_200_OK)
        
        return Response({"message": "Added to favorites.", "is_favorite": True}, status=status.HTTP_201_CREATED)
