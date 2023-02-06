from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django.conf import settings
from accounts.models import Accounts
from .models import DamagePenalty,Hostel


# @receiver(post_save,sender=DamagePenalty)
# def Create_Virtual_Wallet(instance, created, sender, **kwargs):
#     if created:
#         user = Accounts.objects.get(id=instance.tenant)

#         # Virtual_Wallet.objects.create(user=instance.amount_charged)
