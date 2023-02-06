from email.policy import default
from django.db import models
import uuid
import django
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MinLengthValidator
from bookings.models import Bookings

# Create your models here.


# custom validators
def phone_validator(value):
    if len(value) == 12:
        return value
    else:
        raise ValidationError("Make sure your phone number is in 2547XXXXXXXX format")


class Transactions(models.Model):
    Transaction_id = models.CharField(
        max_length=100, primary_key=True, unique=True, default=uuid.uuid4
    )
    amount = models.FloatField()
    sender_name = models.CharField(max_length=100)
    sender_number = models.CharField(max_length=15)
    receiver_number = models.CharField(max_length=15)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.Transaction_id


class MpesaTransactions(models.Model):
    Timestamp = models.DateTimeField(default=django.utils.timezone.now)
    TransactionType = models.CharField(max_length=15, default="CustomerPayBillOnline")
    Amount = models.FloatField()
    PartyA = models.IntegerField(validators=[phone_validator])
    PartyB = models.IntegerField(default=174379)
    PhoneNumber = models.IntegerField(validators=[phone_validator])
    AccountReference = models.CharField(max_length=20)
    TransactionDesc = models.CharField(max_length=20, default="Rent Payments")


class UnconfirmedMpesaStkPush(models.Model):
    payment_status = (
        ("PAID", "PAID"),
        ("CANCELLED", "CANCELLED"),
        ("ERROR", "ERROR"),
        ("IN_PROGRESS", "IN_PROGRES"),
    )

    id = models.CharField(
        max_length=100, primary_key=True, unique=True, default=uuid.uuid1
    )
    booking = models.ForeignKey(Bookings, on_delete=models.DO_NOTHING, null=True)
    MerchantRequestID = models.CharField(max_length=100)
    CheckoutRequestID = models.CharField(max_length=100)
    ResponseDescription = models.CharField(max_length=100)
    CustomerMessage = models.CharField(max_length=100)
    ResponseCode = models.IntegerField()
    amount = models.FloatField()
    Timestamp = models.DateTimeField(default=django.utils.timezone.now)
    is_confirmed = models.BooleanField(default=False)
    status = models.CharField(
        max_length=100, choices=payment_status, default="IN_PROGRESS"
    )

    def __str__(self) -> str:
        return self.id
