from django.contrib import admin
from .models import Bookings, Checkout

# Register your models here.


class BookingAdmin(admin.ModelAdmin):
    list_display = [
        "booking_id",
        "tenant_username",
        "status",
        "room",
        "required_payments",
    ]
    readonly_fields = ["tenant", "booking_id"]


admin.site.register(Bookings, BookingAdmin)


class CheckoutAdmin(admin.ModelAdmin):
    list_display = [
        "checkout_id",
        "booking",
        "amount_paid",
        "is_paid",
    ]
    readonly_fields = ["checkout_id", "is_paid", "amount_paid"]
    list_filter = ["booking"]


admin.site.register(Checkout, CheckoutAdmin)
