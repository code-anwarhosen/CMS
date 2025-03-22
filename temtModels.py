from django.db import models
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.db import transaction

class Contract(models.Model):
    cashValue = models.PositiveIntegerField(help_text="Total cash value")
    hireValue = models.PositiveIntegerField(help_text="Total hire value")
    downPayment = models.PositiveIntegerField(help_text="Down payment amount")
    monthlyPayment = models.PositiveIntegerField(help_text="Monthly payment amount")
    length = models.PositiveIntegerField(help_text="Length of the contract in months")

    cashBalance = models.PositiveIntegerField(help_text="Remaining cash balance", editable=False)
    hireBalance = models.PositiveIntegerField(help_text="Remaining hire balance", editable=False)

    class Meta:
        ordering = ['-id']  # Order contracts by ID descending by default

    def clean(self):
        """
        Custom validation to ensure that the down payment is not greater than the cash or hire value.
        """
        if self.downPayment > self.cashValue:
            raise ValidationError({'downPayment': 'Down payment cannot exceed the cash value.'})
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
                totalPaid = self.payments.aggregate(Sum('amount'))['amount__sum'] or 0
                self.cashBalance = self.cashValue - self.downPayment - totalPaid
                self.hireBalance = self.hireValue - self.downPayment - totalPaid

            super(Contract, self).save(*args, **kwargs)

    def __str__(self):
        return f"Contract #{self.id} - Cash Balance: {self.cashBalance} - Hire Balance: {self.hireBalance}"














from django.db import models
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.db import transaction

class Payment(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='payments')
    date = models.DateField(help_text="Date of the payment")
    receiptId = models.CharField(max_length=100, unique=True, help_text="Receipt ID for the payment")
    amount = models.PositiveIntegerField(help_text="Amount of the payment")

    class Meta:
        ordering = ['date']  # Order payments by date ascending by default

    def __str__(self):
        return f"Payment #{self.id} - Amount: {self.amount} - Date: {self.date}"

# Signal handler for when a Payment is created
@receiver(post_save, sender=Payment)
def update_contract_on_payment_create(sender, instance, created, **kwargs):
    if created:
        contract = instance.contract
        with transaction.atomic():
            contract.cashBalance -= instance.amount
            contract.hireBalance -= instance.amount
            contract.save()

# Signal handler for when a Payment is updated
@receiver(pre_save, sender=Payment)
def update_contract_on_payment_update(sender, instance, **kwargs):
    try:
        old_instance = Payment.objects.get(pk=instance.pk)
        old_amount = old_instance.amount
    except Payment.DoesNotExist:
        old_amount = 0
    
    if instance.amount != old_amount:
        contract = instance.contract
        with transaction.atomic():
            # Reverse the old amount first
            contract.cashBalance += old_amount
            contract.hireBalance += old_amount
            # Apply the new amount
            contract.cashBalance -= instance.amount
            contract.hireBalance -= instance.amount
            contract.save()

# Signal handler for when a Payment is deleted
@receiver(post_delete, sender=Payment)
def update_contract_on_payment_delete(sender, instance, **kwargs):
    contract = instance.contract
    with transaction.atomic():
        contract.cashBalance += instance.amount
        contract.hireBalance += instance.amount
        contract.save()


