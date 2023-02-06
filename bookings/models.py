from datetime import date
import uuid
from django.db import models
from accounts.models import Accounts
from hostels.models import Hostel, Room
import uuid

# Create your models here.


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Bookings(TimeStampMixin):
    statuses = (
        ("REQUESTED", "REQUESTED"),
        ("ACCEPTED", "ACCEPTED"),
        ("VISITED", "VISITED"),
        ("BOOKED", "BOOKED"),
        ("COMPLETED", "COMPLETED"),
        ("CANCELLED", "CANCELLED"),
    )
    booking_id = models.CharField(max_length=130, default=uuid.uuid4, primary_key=True)
    tenant = models.ForeignKey(Accounts, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=50, choices=statuses, default="REQUESTED")
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, default="9305ec4b-8a23-49bf-a2e7-d3d8479bd793"
    )
    reason_for_cancelling = models.CharField(max_length=800, blank=True, null=True)

    @property
    def required_payments(self):
        price = Room.objects.get(id=self.room).pricing
        deposit = Room.objects.get(id=self.room).deposit
        payments = price + deposit
        return payments

    @property
    def tenant_username(self):
        return self.tenant.username

    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"


class Checkout(TimeStampMixin):
    checkout_id = models.CharField(max_length=130, default=uuid.uuid4, primary_key=True)
    booking = models.ForeignKey(Bookings, on_delete=models.CASCADE, default=0)
    amount_paid = models.FloatField(default=0)
    is_paid = models.BooleanField(default=False)


class DamagePenalty(TimeStampMixin):
    penalty_id = models.CharField(max_length=130, default=uuid.uuid4, primary_key=True)
    item_damaged = models.CharField(max_length=80)
    description = models.CharField(max_length=600)
    amount_charged = models.FloatField()
    tenant = models.ForeignKey(Accounts, on_delete=models.DO_NOTHING)
