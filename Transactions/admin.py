from django.contrib import admin
from .models import UnconfirmedMpesaStkPush

# Register your models here.


class unconfirmSTKPushesAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "Timestamp",
        "MerchantRequestID",
        "CheckoutRequestID",
        "ResponseDescription",
        "ResponseCode",
        "amount",
        "is_confirmed",
        "status",
    ]
    readonly_fields = ["amount", "is_confirmed", "status"]
    list_filter = ["is_confirmed", "status"]


admin.site.register(UnconfirmedMpesaStkPush, unconfirmSTKPushesAdmin)
