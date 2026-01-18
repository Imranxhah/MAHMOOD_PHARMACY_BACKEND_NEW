from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, CharWidget
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

class NullableCharWidget(CharWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if value in [None, ""]:
            return None
        return super().clean(value, row, *args, **kwargs)

class ProductResource(resources.ModelResource):
    # Field mapping with the custom widget
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=GetOrCreateForeignKeyWidget(Category, 'name')
    )
    
    barcode = fields.Field(
        column_name='barcode',
        attribute='barcode',
        widget=NullableCharWidget()
    )

    class Meta:
        model = Product
        import_id_fields = ('barcode',) 
        fields = ('name', 'category', 'price', 'stock', 'description', 'is_active', 'generic_name', 'manufacturer', 'strips_in_pack', 'tablets_in_strip', 'pack_price', 'strip_price', 'barcode')

    def get_instance(self, instance_loader, row):
        """
        Custom lookup logic:
        1. Try to find by Barcode (Higher precision).
        2. If not found, fall back to Name (Legacy/Lower precision).
        3. If neither found, return None (Create new).
        """
        barcode_val = row.get('barcode')
        name_val = row.get('name')

        # 1. Try fetching by Barcode first
        if barcode_val:
            try:
                return Product.objects.get(barcode=barcode_val)
            except Product.DoesNotExist:
                pass # Fall through to try Name
            except Product.MultipleObjectsReturned:
                 return Product.objects.filter(barcode=barcode_val).first()

        # 2. Fallback to Name (Legacy/Low Precision)
        if name_val:
            try:
                # Case-insensitive match for name
                return Product.objects.get(name__iexact=name_val)
            except Product.DoesNotExist:
                pass
            except Product.MultipleObjectsReturned:
                return Product.objects.filter(name__iexact=name_val).first()
            
        return None

    def import_field(self, field, obj, row, is_m2m=False, **kwargs):
        """
        Override to prevent overwriting existing data with empty values for specific fields.
        """
        if field.attribute == 'barcode':
            val = row.get('barcode')
            # If the CSV value is empty/None, and the object already has a barcode, SKIP updating it.
            if val in [None, ''] and obj.barcode:
                return
        
        super().import_field(field, obj, row, is_m2m, **kwargs)

    def before_import_row(self, row, **kwargs):
        """
        1. Sanitize 'barcode': Convert empty string to None to avoid UniqueConstraint errors.
        2. Logic: If product exists (found by get_instance logic), ADD the new stock to the existing stock.
        """
        # Ensure empty strings are treated as None for barcode
        if 'barcode' in row and row['barcode'] == '':
            row['barcode'] = None
            
        name = row.get('name')
        new_stock = row.get('stock')
        barcode = row.get('barcode')
        
        product = None
        
        # Re-use the lookup logic to find the product for stock update
        if barcode:
            product = Product.objects.filter(barcode=barcode).first()
        
        if not product and name:
            product = Product.objects.filter(name__iexact=name).first()

        if product and new_stock:
             # If found, add the stocks
            try:
                current_stock = int(product.stock)
                added_stock = int(new_stock)
                row['stock'] = current_stock + added_stock
            except (ValueError, TypeError):
                pass # Invalid integer, ignore
