from django.db import transaction
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, post_delete
from .models import Payment, Account

# Signal handler for when a Payment is about to be saved (pre_save)
@receiver(pre_save, sender=Payment)
def store_old_payment_amount(sender, instance, **kwargs):
    # Only process updates, not new payments
    if not instance._state.adding:
        old_instance = Payment.objects.get(pk=instance.pk)
        instance._old_amount = old_instance.amount
    else:
        instance._old_amount = 0

# Signal handler for when a Payment is saved (post_save)
@receiver(post_save, sender=Payment)
def update_contract_on_payment_create_or_update(sender, instance, created, **kwargs):
    with transaction.atomic():
        contract = instance.contract
        payment_amount = instance.amount
        old_payment_amount = instance._old_amount

        if created:
            # Handle creation: Subtract the new amount
            contract.cashBalance -= payment_amount
            contract.hireBalance -= payment_amount
        
        # Handle update: Reverse the old amount and apply the new amount
        elif old_payment_amount != payment_amount:
            net_difference = old_payment_amount - payment_amount
            contract.cashBalance += net_difference
            contract.hireBalance += net_difference
        contract.save()


# Signal handler for when a Payment is deleted
@receiver(post_delete, sender=Payment)
def update_contract_on_payment_delete(sender, instance, **kwargs):
    contract = instance.contract
    with transaction.atomic():
        contract.cashBalance += instance.amount
        contract.hireBalance += instance.amount
        contract.save()


# Signal handler for when a Account is deleted
@receiver(post_delete, sender=Account)
def delete_related_models_when_account_deleted(sender, instance, **kwargs):
    contract = getattr(instance, 'contract', None)
    if contract:
        contract.delete()
