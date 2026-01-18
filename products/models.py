from django.db import models
from django.conf import settings
from config.utils import compress_image

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old = Category.objects.get(pk=self.pk)
                if old.image != self.image:
                    compress_image(self.image)
            except Category.DoesNotExist:
                pass
        else:
            compress_image(self.image)
        super().save(*args, **kwargs)

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    generic_name = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Packaging details
    strips_in_pack = models.PositiveIntegerField(blank=True, null=True, verbose_name="Strips in Pack")
    tablets_in_strip = models.PositiveIntegerField(blank=True, null=True, verbose_name="Tablets in Strip")
    pack_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Price per Pack")
    strip_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Price per Strip")
    manufacturer = models.CharField(max_length=255, blank=True, null=True, verbose_name="Manufacturer")
    barcode = models.CharField(max_length=255, unique=True, blank=True, null=True, verbose_name="Barcode")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old = Product.objects.get(pk=self.pk)
                if old.image != self.image:
                    compress_image(self.image)
            except Product.DoesNotExist:
                pass
        else:
            compress_image(self.image)
        super().save(*args, **kwargs)

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='favorites', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='favorited_by', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user} - {self.product}"
