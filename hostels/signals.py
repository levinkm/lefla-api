from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django.conf import settings
from accounts.models import Accounts
from .models import Virtual_Wallet,Landlord

User = settings.AUTH_USER_MODEL

@receiver(post_save,sender=Accounts)
def Create_Virtual_Wallet(instance, created, sender, **kwargs):
    if created:
        Virtual_Wallet.objects.create(user=instance)

@receiver(post_save,sender=Accounts)
def Make_Landlord(instance,sender, **kwargs):
    if Accounts.objects.filter(email=instance,is_landlord=True):
        Landlord.objects.create(user=instance)

@receiver(post_save,sender=Accounts)
def Make_Landlord(instance,sender, **kwargs):
    '''To delete Landlord when the is_landlord checkbox is unmarked'''
    if Accounts.objects.filter(email=instance,is_landlord=False):
        Landlord.objects.filter(user=instance).delete()

@receiver(post_delete,sender=Landlord)
def Make_Landlord(instance,sender, **kwargs):
    '''To change the is_landlord boolean back to false when Landlord is deleted'''
    a = Accounts.objects.get(username=instance)
    a.is_landlord = False
    a.save()



