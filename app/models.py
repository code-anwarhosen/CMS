from django.db import models

import os
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile


defaultAvatar = 'customer/avatars/default.png'
def customerAvatarPath(instance, filename):
    folder_name = f"customer/avatars/"
    ext = filename.split('.')[-1]
    new_filename = f"avatar_{instance.name}.{ext}"
    return os.path.join(folder_name, new_filename)

def compressAvatar(image):
    """Compress and resize the image to ensure it doesn't exceed the size limit."""
    img = Image.open(image)
    img = img.convert('RGB')  # Ensure consistent compression format

    # Resize the image while maintaining aspect ratio, max dimensions 500x500
    max_size = (500, 500)
    img.thumbnail(max_size, Image.LANCZOS)

    # Save the compressed image to memory
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=90)
    buffer.seek(0)

    # Return the new compressed image
    return InMemoryUploadedFile(buffer, None, image.name, 'image/jpeg', buffer.tell(), None)

class Customer(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female')
    ]
    GUARDIAN_TYPES = [
        ('father', 'Father'),
        ('husband', 'Husband'),
    ]

    name = models.CharField(max_length=100) #required
    age = models.PositiveIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    avatar = models.ImageField(upload_to=customerAvatarPath, blank=True, null=True)
    phone = models.CharField(max_length=14, help_text="Format: +880XXXXXXXXXX") #required
    occupation = models.CharField(max_length=100, blank=True, null=True)
    
    guardian_type = models.CharField(max_length=10, choices=GUARDIAN_TYPES, blank=True, null=True)
    guardian_name = models.CharField(max_length=100, blank=True, null=True)

    address = models.CharField(max_length=500) #required
    location_mark = models.CharField(max_length=500, blank=True, null=True)

    def _avatar_needs_compression(self):
        """ Check if the avatar needs to be compressed (only if it has changed). """
        if not self.pk:  # New profile, avatar needs processing
            return True
        old_avatar = Customer.objects.filter(pk=self.pk).first()
        return old_avatar.avatar != self.avatar if old_avatar else True

    def save(self, *args, **kwargs):
        if self.avatar and self._avatar_needs_compression():
            if self.avatar.name != defaultAvatar:
                self.avatar = compressAvatar(self.avatar)
                
        if not self.avatar:
            self.avatar = defaultAvatar
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
