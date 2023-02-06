from django.contrib import admin
from .models import (
    Hostel,
    Category,
    RoomImages,
    Transactions,
    Virtual_Wallet,
    Landlord,
    Amenities,
    Room,
)

# Register your models here.
admin.site.register(Hostel)
admin.site.register(Category)
admin.site.register(Transactions)
admin.site.register(Virtual_Wallet)
admin.site.register(Landlord)
admin.site.register(Amenities)
admin.site.register(Room)


class ImagesAdmin(admin.ModelAdmin):
    list_display = ["id", "image_url_1", "image_url_2", "image_url_3", "image_url_4"]


admin.site.register(RoomImages, ImagesAdmin)
