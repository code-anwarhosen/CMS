from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction


from .utils import defaultAvatar, GUARDIAN_TYPES, OCCUPATIONS, ACCOUNT_STATUSES, PRODUCT_CATEGORIES
from .utils import compressAvatar, customerAvatarPath


class Customer(models.Model):
    uid = models.BigIntegerField(primary_key=True, unique=True, editable=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='customers')

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
        if not self.uid: #Set custom uid
            with transaction.atomic():  # Ensures safe execution
                max_uid = Customer.objects.aggregate(models.Max('uid'))['uid__max']
                self.uid = (max_uid or 1000000) + 1
        

        #Compress avatar image on condition
        if self.avatar and self._avatar_needs_compression():
            if self.avatar.name != defaultAvatar:
                self.avatar = compressAvatar(self.avatar)
        
        if not self.avatar:
            self.avatar = defaultAvatar
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

    cashBalance = models.IntegerField(help_text="Remaining cash balance", editable=False)
    hireBalance = models.IntegerField(help_text="Remaining hire balance", editable=False)

    @property
    def totalPaid(self):
        payments = self.payments.aggregate(models.Sum('amount'))['amount__sum'] or 0
        return payments + self.downPayment

    class Meta:
        ordering = ['-id']

    def clean(self):
        if self.downPayment > self.hireValue:
            raise ValidationError({'downPayment': 'Down payment cannot exceed the hire value.'})

    def save(self, *args, **kwargs):
        # Validate contract before saving
        self.full_clean()

        # Start transaction to ensure atomicity
        with transaction.atomic():
            # Calculate balance on creation or update
            if not self.pk:  # Contract is being created
                self.cashBalance = self.cashValue - self.downPayment
                self.hireBalance = self.hireValue - self.downPayment

            else:  # Contract is being updated
                self.cashBalance = self.cashValue - self.totalPaid
                self.hireBalance = self.hireValue - self.totalPaid

            super().save(*args, **kwargs)

    def __str__(self):
        if hasattr(self, 'account'):
            return f"Account: {self.account.number}"
        return f"Contract {self.id}"



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
        if self.amount > self.contract.hireBalance:
            raise ValidationError("Payment amount exceeds remaining balance.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)



class Guarantor(models.Model):
    uid = models.BigIntegerField(primary_key=True, unique=True, editable=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='guarantors')
    
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
            with transaction.atomic(): # Ensures safe execution
                max_uid = Guarantor.objects.aggregate(models.Max('uid'))['uid__max']
                self.uid = (max_uid or 5000000) + 1
        super().save(*args, **kwargs)



class Account(models.Model):
    number = models.CharField(max_length=10, primary_key=True, unique=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='accounts')
    guarantors = models.ManyToManyField(Guarantor, related_name='accounts')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    contract = models.OneToOneField(Contract, on_delete=models.SET_NULL, null=True, related_name='account')

    saleDate = models.DateField()
    status = models.CharField(max_length=10, choices=ACCOUNT_STATUSES, default='Active')

    def __str__(self):
        return self.number

