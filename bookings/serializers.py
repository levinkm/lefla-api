from rest_framework import serializers
from .models import Bookings, Checkout, DamagePenalty
from hostels.serializers import (
    HosteleExtrarializer,
    RoomSerializerRequests,
    UserSeializer,
)


class BookingSerializer(serializers.ModelSerializer):
    tenant = UserSeializer()
    status = serializers.CharField(max_length=50)
    room = RoomSerializerRequests()

    class Meta:
        model = Bookings
        fields = [
            "booking_id",
            "created_at",
            "tenant",
            "status",
            "room",
        ]


class BookingAcceptanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookings
        fields = ["booking_id", "status", "reason_for_cancelling"]
        extra_kwargs = {"booking_id": {"required": True, "allow_blank": False}}
        extra_kwargs = {"status": {"required": True, "allow_blank": False}}


class BookingPostSerializer(serializers.Serializer):
    PhoneNumber = serializers.CharField(max_length=15)

    class Meta:
        fields = ["PhoneNumber"]


class BookHostelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookings
        fields = ["room", "tenant"]
        read_only_fields = ["status", "reason_for_cancelling", "booking_id"]


class CheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkout
        fields = "__all__"


class DamagePenaltySerializer(serializers.ModelSerializer):
    class Meta:
        model = DamagePenalty
        fields = "__all__"


class VisitRequestSerializer(serializers.ModelSerializer):
    room = RoomSerializerRequests()
    tenant = UserSeializer()

    class Meta:
        model = Bookings
        fields = [
            "booking_id",
            "tenant",
            "status",
            "room",
        ]
