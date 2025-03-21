from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction

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



GUARDIAN_TYPES = [
    ('Father', 'Father'),
    ('Husband', 'Husband')
]
OCCUPATIONS = [
    ('Job', 'Job'),
    ('GovtJob', 'Govt. Job'),
    ('Business', 'Business'),
    ('Student', 'Student'),
    ('Housewife', 'Housewife'),

    ('Teacher', 'Teacher'),
    ('Doctor', 'Doctor'),
    ('Other', 'Other'),
]

PRODUCT_CATEGORIES = [
    ('LED_TV', 'LED TV'),
    ('REF', 'REF'),
    ('FREEZER', 'FREEZER'),
    ('WM', 'WM'),
    ('AC', 'AC'),
]

ACCOUNT_STATUSES = [
    ('Active', 'Active'),
    ('Closed', 'Closed'),
]

class Customer(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='customers')
    uid = models.BigAutoField(primary_key=True, unique=True, editable=False)

    name = models.CharField(max_length=100) #required
    age = models.PositiveIntegerField(blank=True, null=True)
    avatar = models.ImageField(upload_to=customerAvatarPath, blank=True, null=True, default=defaultAvatar)
    phone = models.CharField(max_length=14, help_text="Format: +880XXXXXXXXXX") #required
    occupation = models.CharField(max_length=100, choices=OCCUPATIONS, blank=True, null=True)
    
    guardianType = models.CharField(max_length=10, choices=GUARDIAN_TYPES, blank=True, null=True)
    guardianName = models.CharField(max_length=100, blank=True, null=True)

    address = models.CharField(max_length=500) #required
    locationMark = models.CharField(max_length=500, blank=True, null=True)

    def _avatar_needs_compression(self):
        """ Check if the avatar needs to be compressed (only if it has changed). """
        if not self.pk:  # New profile, avatar needs processing
            return True
        old_avatar = Customer.objects.filter(pk=self.pk).first()
        return old_avatar.avatar != self.avatar if old_avatar else True

    def save(self, *args, **kwargs):
        #Set custom uid
        if not self.uid:
            lastObj = Customer.objects.order_by('-uid').first()
            if lastObj:
                self.uid = lastObj.uid + 1
            else:
                self.uid = 1000001

        #Compress avatar image on condition
        if self.avatar and self._avatar_needs_compression():
            if self.avatar.name != defaultAvatar:
                self.avatar = compressAvatar(self.avatar)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-uid']



class Model(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    
class Product(models.Model):
    category = models.CharField(max_length=100, choices=PRODUCT_CATEGORIES)
    model = models.OneToOneField(Model, on_delete=models.CASCADE, null=True, blank=True, related_name='product')

    def __str__(self):
        return f'{self.category} : {self.model}'
    



class Contract(models.Model):
    cashValue = models.PositiveIntegerField(help_text="Total cash value")
    hireValue = models.PositiveIntegerField(help_text="Total hire value")
    downPayment = models.PositiveIntegerField(help_text="Down payment amount")
    monthlyPayment = models.PositiveIntegerField(help_text="Monthly payment amount")
    length = models.PositiveIntegerField(help_text="Length of the contract in months")

    cashBalance = models.PositiveIntegerField(help_text="Remaining cash balance", editable=False)
    hireBalance = models.PositiveIntegerField(help_text="Remaining hire balance", editable=False)

    def __str__(self):
        if hasattr(self, 'account'):
            return f"Account: {self.account.number}"
        return f"Contract {self.id}"

    class Meta:
        ordering = ['-id']

    def clean(self):
        # Validate downPayment does not exceed cashValue or hireValue
        if self.downPayment > self.cashValue or self.downPayment > self.hireValue:
            raise ValidationError("Down payment cannot exceed cash or hire value.")

        # Validate length is a positive integer
        if self.length <= 0:
            raise ValidationError("Length must be a positive integer.")

    def save(self, *args, **kwargs):
        # Calculate monthlyPayment
        if self.length > 0:
            self.monthlyPayment = self.cashValue // self.length
        else:
            raise ValidationError("Length must be a positive integer to calculate monthly payment.")

        # Calculate balances
        if not self.pk:  # New contract
            self.cashBalance = self.cashValue - self.downPayment
            self.hireBalance = self.hireValue - self.downPayment
        else:  # Existing contract
            # Use aggregation to get the sum of payments, defaulting to 0 if no payments exist
            total_payments = self.payments.aggregate(total=models.Sum('amount'))['total'] or 0
            self.cashBalance = self.cashValue - self.downPayment - total_payments
            self.hireBalance = self.hireValue - self.downPayment - total_payments
        super().save(*args, **kwargs)


class Payment(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='payments')
    date = models.DateField(help_text="Date of the payment")
    receiptId = models.CharField(max_length=100, unique=True, help_text="Receipt ID for the payment")
    amount = models.PositiveIntegerField(help_text="Amount of the payment")

    def __str__(self):
        if hasattr(self.contract, 'account'):
            return f"Account: {self.contract.account.number}"
        return f"Payment {self.receiptId} - {self.amount}"

    class Meta:
        ordering = ['-date']

    def clean(self):
        # Validate payment amount does not exceed remaining balances
        if self.amount > self.contract.cashBalance or self.amount > self.contract.hireBalance:
            raise ValidationError("Payment amount exceeds remaining balance.")

    @transaction.atomic
    def save(self, *args, **kwargs):
        if not self.pk:  # New payment
            # Update balances using F expressions to avoid race conditions
            Contract.objects.filter(pk=self.contract.pk).update(
                cashBalance=models.F('cashBalance') - self.amount,
                hireBalance=models.F('hireBalance') - self.amount
            )
        else:  # Updated payment
            old_payment = Payment.objects.get(pk=self.pk)
            old_amount = old_payment.amount
            # Adjust balances based on the difference between old and new amounts
            Contract.objects.filter(pk=self.contract.pk).update(
                cashBalance=models.F('cashBalance') + old_amount - self.amount,
                hireBalance=models.F('hireBalance') + old_amount - self.amount
            )

        super().save(*args, **kwargs)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        # Restore balances before deleting the payment
        Contract.objects.filter(pk=self.contract.pk).update(
            cashBalance=models.F('cashBalance') + self.amount,
            hireBalance=models.F('hireBalance') + self.amount
        )
        # Now delete the payment
        super().delete(*args, **kwargs)


class Guarantor(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='guarantors')
    uid = models.BigAutoField(primary_key=True, unique=True, editable=False)
    
    name = models.CharField(max_length=100)  #required
    phone = models.CharField(max_length=14, help_text="Format: +880XXXXXXXXXX", blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-uid']

    def save(self, *args, **kwargs):
        if not self.uid:
            lastObj = Guarantor.objects.order_by('-uid').first()
            if lastObj:
                self.uid = lastObj.uid + 1
            else:
                self.uid = 5000001
        super().save(*args, **kwargs)



class Account(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    number = models.CharField(max_length=10, unique=True, primary_key=True)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='accounts')
    guarantors = models.ManyToManyField(Guarantor, related_name='accounts')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    contract = models.OneToOneField(Contract, on_delete=models.SET_NULL, null=True, related_name='account')

    saleDate = models.DateField()
    status = models.CharField(max_length=10, choices=ACCOUNT_STATUSES, default='Active')

    def __str__(self):
        return self.number
    