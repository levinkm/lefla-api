from email.mime import image
from email.policy import default


from unicodedata import name
from django.db import models
from django.forms import SelectDateWidget
import uuid
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.utils import timezone
from ckeditor.fields import RichTextField
from PIL import Image

# from graphql import print_location

# Create your models here.
Accounts = settings.AUTH_USER_MODEL


class Address(models.Model):
    place_name = models.CharField(max_length=70, default="")
    town = models.CharField(max_length=70, default="")
    lon = models.DecimalField(null=True, default=0, max_digits=10, decimal_places=7)
    lat = models.DecimalField(null=True, default=0, max_digits=10, decimal_places=7)

    class Meta:

        abstract = True


class Category(models.Model):
    category = models.CharField(max_length=50, primary_key=True, unique=True)

    def __str__(self) -> str:
        return self.category


class Amenities(models.Model):
    wifi = models.BooleanField(default=False)
    water = models.BooleanField(default=False)
    dirt_collection = models.BooleanField(default=False)
    gymn = models.BooleanField(default=False)
    food = models.BooleanField(default=False)
    brddings = models.BooleanField(default=False)
    transport = models.BooleanField(default=False)
    entertainment = models.BooleanField(default=False)
    security = models.BooleanField(default=False)
    laundry = models.BooleanField(default=False)


class Landlord(models.Model):
    user = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)

    def __str__(self) -> str:
        return self.user.username


class Hostel(Address):
    # rooms_available = models.IntegerField(default=0)

    id = models.AutoField(primary_key=True)
    hostel_name = models.CharField(max_length=150, unique=True)
    hostel_description = models.CharField(max_length=1000)
    hostel_rating = models.IntegerField(
        validators=[
            MaxValueValidator(5, "Should be less than 5"),
            MinValueValidator(1, "Should be more than 0"),
        ],
        default=1,
    )
    avilable_amenities = models.ForeignKey(Amenities, models.CASCADE)
    landlord = models.ForeignKey(Landlord, on_delete=models.CASCADE)
    lefla_for_rental_collection = models.BooleanField(default=False)
    hostel = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.hostel_name

    @property
    def hostel_rooms(self):
        hostels = self.room_set.all()
        data = hostels.values()
        check = []

        for hostel in data:
            images = RoomImages.objects.filter(room_id=hostel["id"])
            res = images.values()

            data1 = {}
            data1["hostel-room"] = hostel
            data1["image"] = res
            check.append(data1)

        return check

    @property
    def categories_available(self):
        categories = self.room_set.order_by().values("room_type").distinct()
        return categories

    @property
    def number_of_rooms_available(self):
        global rooms
        rooms = Room.objects.filter(
            hostel_id=self.id, is_booked=False, is_occupied=False
        )
        context = {"count": rooms.count, "rooms": rooms.values("id")}

        return rooms.count

    @property
    def rooms_available(self):
        return rooms.values(
            "id",
        )


class Virtual_Wallet(models.Model):
    user = models.OneToOneField(Accounts, on_delete=models.CASCADE)
    available_amount = models.FloatField(default=0)
    wallet_id = models.CharField(
        max_length=100, primary_key=True, unique=True, default=uuid.uuid4
    )
    amount_owed = models.FloatField(default=0)

    def __str__(self) -> str:
        return self.user.username


class Transactions(models.Model):
    Transaction_id = models.CharField(
        max_length=100, primary_key=True, unique=True, default=uuid.uuid4
    )
    amount = models.FloatField()
    sender = models.CharField(max_length=100)
    receiver = models.CharField(max_length=15)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.Transaction_id


class Room(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, max_length=250)
    hostel_id = models.ForeignKey(
        Hostel, verbose_name=("hostel"), on_delete=models.CASCADE
    )
    room_type = models.ForeignKey(
        Category, on_delete=models.CASCADE, default="Other", null=True
    )
    pricing = models.FloatField()
    offer = models.FloatField()
    deposit = models.IntegerField()
    service_fee = models.IntegerField()
    is_booked = models.BooleanField(default=False)
    is_occupied = models.BooleanField(default=False)
    # number_of_rooms_avilable = models.IntegerField(default=0)

    def __str__(self) -> str:
        name = f"{self.hostel_id.hostel_name}-{self.room_type}"
        return name

    @property
    def total_amount(self):
        total = self.pricing + self.deposit + self.service_fee
        return total

    @property
    def rooms_images(self):
        pics = self.roomimages_set.all()

        return pics.values()


class RoomImages(models.Model):
    room_id = models.OneToOneField(Room, models.CASCADE)
    id = models.CharField(
        max_length=100, primary_key=True, unique=True, default=uuid.uuid4
    )
    image_url_1 = models.ImageField(upload_to="hostel_images")
    image_url_2 = models.ImageField(upload_to="hostel_images")
    image_url_3 = models.ImageField(upload_to="hostel_images")
    image_url_4 = models.ImageField(upload_to="hostel_images")
