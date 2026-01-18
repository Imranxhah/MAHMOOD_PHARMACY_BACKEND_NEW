from rest_framework import serializers
from .models import Category, Product, Favorite

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_name', 'name', 
            'generic_name', 'description', 'manufacturer', 'price', 'stock', 'image', 
            'is_active', 'created_at', 'updated_at',
            'strips_in_pack', 'tablets_in_strip', 'pack_price', 'strip_price',
            'is_favorite'
        ]

    def get_is_favorite(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, product=obj).exists()
        return False

class FavoriteSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = Favorite
        fields = ['id', 'product', 'product_id', 'created_at']
        read_only_fields = ['user']

class ProductBulkUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
