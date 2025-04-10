# ++++++++++++++++ MODELS CONSTANT +++++++++++++++++++
defaultAvatar = 'customer/avatars/default.png'

GUARDIAN_TYPES = [
    ('Father', 'Father'),
    ('Husband', 'Husband')
]

OCCUPATIONS = [
    ('Job', 'Job'),
    ('Govt-Job', 'Govt-Job'),
    ('Business', 'Business'),
    ('Student', 'Student'),
    ('Housewife', 'Housewife'),
    ('Teacher', 'Teacher'),
    ('Doctor', 'Doctor'),
    ('Plumber', 'Plumber'),
    ('Technician', 'Technician'),
    ('Electrician', 'Electrician'),
    ('Others', 'Others')
]


PRODUCT_CATEGORIES = [
    ('Television', 'Television'),
    ('Refrigerator', 'Refrigerator'),
    ('Deep Freezer', 'Deep Freezer'),
    ('Air Conditioner', 'Air Conditioner'),
    ('Washing Machine', 'Washing Machine'),
    ('Microwave Oven', 'Microwave Oven'),
    ('Sewing Machine', 'Sewing Machine'),
    ('Computer', 'Computer'),
    ('Others', 'Others')
]




# ++++++++++++++++ MODELS UTILITY +++++++++++++++++++
import os
from pathlib import Path
from django.core.exceptions import ValidationError

from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile



def compressAvatar(image):
    if not image:
        return image  # Return the original if no image is provided
    
    img = Image.open(image)
    if image.size < 200 * 1024:  # 200 KB threshold
        return image  # No need to compress
    
    max_file_size = 5 * 1024 * 1024  # 5MB limit
    if image.size > max_file_size:
        raise ValidationError("Image file size should not exceed 5MB.")
    
    if img.format not in ['JPG', 'JPEG', 'PNG']:
        raise ValidationError(f"Unsupported image format: {img.format}")

    img = img.convert('RGB')  # Ensure it's a standard format for JPEG compression
    
    # Resize while maintaining aspect ratio (Max: 500x500)
    max_size = (500, 500)
    img.thumbnail(max_size, Image.LANCZOS)

    # Save the compressed image to memory with better quality
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=90, optimize=True, progressive=True)
    buffer.seek(0)

    # Return as InMemoryUploadedFile to save to the model's ImageField
    return InMemoryUploadedFile(buffer, None, image.name, 'image/jpeg', buffer.tell(), None)



def customerAvatarPath(instance, filename):
    folder_name = f"customer/avatars/"
    ext = Path(filename).suffix  # Extracts file extension

    new_filename = f"avatar_{instance.name}{ext}"
    return str(Path(folder_name) / new_filename)

