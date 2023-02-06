from rest_framework import serializers
from .models import Amenities, Hostel, Landlord, Room, Virtual_Wallet, RoomImages
from django.conf import settings
from accounts.models import Accounts


class UserSeializer(serializers.ModelSerializer):
    class Meta:
        model = Accounts
        fields = (
            "email",
            "username",
            "phonenumber",
            "fullname",
            "picture",
        )


class HostelImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomImages
        fields = "__all__"


class LandLordSerializer(serializers.ModelSerializer):
    user = UserSeializer()

    class Meta:

        model = Landlord
        fields = (
            "id",
            "user",
        )

    def get_photo_url(self, obj):
        request = self.context.get("request")
        photo_url = obj.fingerprint.url
        return request.build_absolute_uri(photo_url)


class WalletSerializer(serializers.ModelSerializer):
    user = UserSeializer()

    class Meta:
        model = Virtual_Wallet
        fields = "__all__"


class AvilableAmenitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenities
        fields = "__all__"


class RoomsAvalibaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            "id",
            "room_type",
        ]


class Hostelerializer(serializers.ModelSerializer):
    landlord = LandLordSerializer()
    avilable_amenities = AvilableAmenitiesSerializer()
    # rooms_available = RoomsAvalibaleSerializer()

    class Meta:
        model = Hostel
        fields = (
            "id",
            "number_of_rooms_available",
            "rooms_available",
            "hostel_name",
            "hostel_description",
            "hostel_rating",
            "avilable_amenities",
            "landlord",
            "lon",
            "lat",
            "town",
            "place_name",
            # "categories_available",
            "lefla_for_rental_collection",
        )

    def get_photo_url(self, obj):
        request = self.context.get("request")
        photo_url = obj.fingerprint.url
        return request.build_absolute_uri(photo_url)


class HostelSearcherializer(serializers.Serializer):
    max_price = serializers.IntegerField()
    min_price = serializers.IntegerField()
    hostel_rating = serializers.IntegerField()
    hostel_name = serializers.CharField(max_length=150)
    place_name = serializers.CharField(max_length=150)
    town = serializers.CharField(max_length=150)

    class Meta:
        fields = (
            "hostel_name",
            "hostel_rating",
            "place_name",
            "town",
            "max_price",
            "min_price",
        )


class HostelAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel

        fields = (
            "number_of_rooms_available",
            "hostel_name",
            "hostel_description",
            "hostel_rating",
            "avilable_amenities",
            "town",
            "landlord",
            "lon",
            "lat",
            "place_name",
            "hostel_rooms",
        )

    def get_photo_url(self, obj):
        request = self.context.get("request")
        photo_url = obj.fingerprint.url
        return request.build_absolute_uri(photo_url)


class HosteleExtrarializer(serializers.ModelSerializer):
    landlord = LandLordSerializer()
    avilable_amenities = AvilableAmenitiesSerializer()

    class Meta:
        model = Hostel
        fields = (
            "number_of_rooms_available",
            "hostel_name",
            "hostel_description",
            "hostel_rating",
            "avilable_amenities",
            "town",
            "landlord",
            "lon",
            "lat",
            "place_name",
            "hostel_rooms",
            "hostel",
            "categories_available",
            "lefla_for_rental_collection",
        )

    def get_photo_url(self, obj):
        request = self.context.get("request")
        photo_url = obj.fingerprint.url
        return request.build_absolute_uri(photo_url)


class RoomSerializer(serializers.ModelSerializer):
    hostel_id = Hostelerializer()

    class Meta:
        model = Room
        fields = [
            "id",
            "room_type",
            "pricing",
            "offer",
            "deposit",
            "service_fee",
            "is_booked",
            "is_occupied",
            "rooms_images",
            "hostel_id",
        ]

    def get_photo_url(self, obj):
        request = self.context.get("request")
        photo_url = obj.fingerprint.url
        return request.build_absolute_uri(photo_url)


# --------------------------------------------------------------------------------------------------------


class HostelerializerRequests(serializers.ModelSerializer):
    class Meta:
        model = Hostel

        fields = (
            "number_of_rooms_available",
            "id",
            "hostel_name",
            "town",
            "place_name",
            "lefla_for_rental_collection",
        )


class RoomSerializerRequests(serializers.ModelSerializer):
    hostel_id = HostelerializerRequests()

    class Meta:
        model = Room
        fields = [
            "id",
            "room_type",
            "is_booked",
            "is_occupied",
            "hostel_id",
        ]

    def get_photo_url(self, obj):
        request = self.context.get("request")
        photo_url = obj.fingerprint.url
        return request.build_absolute_uri(photo_url)


class TopUpWalletSerializer(serializers.Serializer):
    Amount = serializers.IntegerField()
    PhoneNumber = serializers.CharField(max_length=20)
    wallet_id = serializers.CharField(max_length=55)

    class Meta:
        fields = ["Amount", "PhoneNumber", "wallet_id"]
