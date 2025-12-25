from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Product, Category

class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        fields = ('id', 'name')
        import_id_fields = ('name',)

    def get_instance(self, instance_loader, row):
        """
        Override to perform case-insensitive lookup for existing Categories.
        If CSV has 'devices' and DB has 'Devices', we return 'Devices'.
        """
        name = row.get('name')
        if name:
            try:
                # Try case-insensitive exact match
                return Category.objects.get(name__iexact=name)
            except Category.DoesNotExist:
                return None
            except Category.MultipleObjectsReturned:
                # Fallback: just return the first one found (edge case)
                return Category.objects.filter(name__iexact=name).first()
        return None

# Custom Widget: Searches for Category by name (Case-Insensitive). If not found, CREATES it.
class GetOrCreateForeignKeyWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if value:
            # 1. Try to find existing category (Case Insensitive)
            try:
                return self.model.objects.get(name__iexact=value)
            except self.model.DoesNotExist:
                # 2. If not found, create it (using the original casing from file)
                return self.model.objects.create(name=value)
            except self.model.MultipleObjectsReturned:
                 return self.model.objects.filter(name__iexact=value).first()
        return None

class ProductResource(resources.ModelResource):
    # Field mapping with the custom widget
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=GetOrCreateForeignKeyWidget(Category, 'name')
    )

    class Meta:
        model = Product
        # CRITICAL: This tells Django to use 'name' to look for duplicates, not ID.
        import_id_fields = ('name',)
        # whitelist fields to import
        fields = ('name', 'category', 'price', 'stock', 'description', 'is_active')

    def get_instance(self, instance_loader, row):
        """
        Case-insensitive lookup for Products (e.g., 'panadol' matches 'Panadol').
        """
        name = row.get('name')
        if name:
            try:
                return Product.objects.get(name__iexact=name)
            except Product.DoesNotExist:
                return None
            except Product.MultipleObjectsReturned:
                return Product.objects.filter(name__iexact=name).first()
        return None

    def before_import_row(self, row, **kwargs):
        """
        Logic: If product exists, ADD the new stock to the existing stock.
        """
        name = row.get('name')
        new_stock = row.get('stock')
        
        if name and new_stock:
            # Try to find the existing product using our case-insensitive logic
            try:
                product = Product.objects.get(name__iexact=name)
                # If found, add the stocks
                try:
                    current_stock = int(product.stock)
                    added_stock = int(new_stock)
                    row['stock'] = current_stock + added_stock
                except ValueError:
                    pass # Invalid integer in CSV or DB, ignore
            except Product.DoesNotExist:
                pass # New product, keep row['stock'] as is
