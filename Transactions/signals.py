from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .utils import mpesaExpressQuery
from time import sleep
from bookings.models import Bookings, Checkout
from hostels.models import Virtual_Wallet
from .tasks import checkMpesa

from .models import UnconfirmedMpesaStkPush


@receiver(post_save, sender=UnconfirmedMpesaStkPush)
def checkMpesaSTKPush(instance, created, sender, **kwargs):
    checkMpesa(instance, created, **kwargs)
