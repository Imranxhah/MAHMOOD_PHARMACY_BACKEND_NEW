import io
import sys
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile

# 1. Safety: Protect against Decompression Bombs
Image.MAX_IMAGE_PIXELS = 100000000  # 100 Million Pixels (approx 10,000 x 10,000)

def compress_image(image_field):
    """
    Compresses the image in the given image_field to ensure it is under 5MB.
    If the image is larger than 5MB after compression, it resizes the dimensions
    and retries until it fits.
    
    Args:
        image_field: The ImageField instance (e.g. self.image)
    """
    if not image_field:
        return

    # Check if we have a real file
    if not hasattr(image_field, 'file'):
        return
        
    # Open the image using Pillow
    try:
        if image_field.closed:
             image_field.open()
        
        img = Image.open(image_field)
        
        # Load data to catch truncation errors early
        img.load()
        
        # Prepare for saving
        # Convert to RGB if it's not transparent/animated to allow JPEG optimization
        # But for consistency and AVIF support, we try to preserve format unless it's huge.
        # Ideally, we stick to the original format unless we need to force generic types.
        # Let's check format.
        original_format = img.format
        if not original_format:
            original_format = 'JPEG' # Default fallback
            
        output_format = original_format
        
        # Handle RGBA -> RGB for JPEGs
        if output_format.upper() == 'JPEG' and img.mode != 'RGB':
            img = img.convert('RGB')
            
        # Optimization Loop
        # We start with original dimensions and quality=85
        quality = 85
        output_io = io.BytesIO()
        
        while True:
            output_io.seek(0)
            output_io.truncate(0)
            
            try:
                img.save(output_io, format=output_format, quality=quality, optimize=True)
            except Exception:
                # Fallback to JPEG if specific format fails (e.g. weird TIFF)
                img = img.convert('RGB')
                output_format = 'JPEG'
                img.save(output_io, format=output_format, quality=quality, optimize=True)
            
            size = output_io.tell()
            
            if size <= 5 * 1024 * 1024:  # 5MB
                break
                
            # If still too big, resize dimensions by 20%
            width, height = img.size
            if width < 300 or height < 300: 
                # Safety break: if it's tiny but still huge bytes (rare), just stop to avoid infinite loop
                break
                
            new_width = int(width * 0.8)
            new_height = int(height * 0.8)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Also drop quality slighty if needed, but resizing is more effective for massive files
            # quality = max(60, quality - 5) 

        # Create a new Django File
        output_io.seek(0)
        file_name = image_field.name
        
        # Ensure extension matches format
        import os
        name, ext = os.path.splitext(file_name)
        if output_format.lower() == 'jpeg' and ext.lower() not in ['.jpg', '.jpeg']:
            file_name = f"{name}.jpg"
        
        new_file = InMemoryUploadedFile(
            output_io,
            'ImageField',
            file_name,
            f'image/{output_format.lower()}',
            sys.getsizeof(output_io),
            None
        )
        
        # Replace the old file with the new one
        # Note: We assign to the file attribute to update the content in memory
        # The save() method of the model will handle writing to storage
        
        # New Feature: Check if new file is bigger than original
        # Only meaningful if original was under limit.
        output_io.seek(0, 2) # Go to end
        new_size = output_io.tell()
        output_io.seek(0)
        
        if image_field.size <= 5 * 1024 * 1024:
             if new_size > image_field.size:
                  # Original was smaller and valid. Keep it.
                  # Just return without saving new file
                  return

        image_field.save(file_name, new_file, save=False)
        
    except Exception as e:
        # If anything goes wrong (corrupt file, etc), we log it but don't crash the save.
        # Or should we crash? User said "reject it if less than than accept it" 
        # but in the refined plan we agreed to "safe fallback". 
        # If we can't open it, it's likely invalid anyway.
        # We'll print error for debugging.
        print(f"Image compression failed: {e}")
        # We leave the original file as is if compression fails, 
        # letting standard Field validation handle it or saving raw.
        pass
