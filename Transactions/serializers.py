from rest_framework import serializers
from .models import MpesaTransactions
from rest_framework.exceptions import ValidationError


class MpesaSerializer(serializers.ModelSerializer):
    booking = serializers.CharField(max_length=100)

    class Meta:
        model = MpesaTransactions
        fields = ("Amount", "PhoneNumber", "booking")

    def validate(self, attrs):
        if len(attrs["PhoneNumber"]) == 12:
            return attrs
        else:
            raise ValidationError(
                "Make sure your phone number is in 2547XXXXXXXX format"
            )

    def create(self, validated_data):
        MpesaT = MpesaTransactions.objects.create(
            Amount=validated_data.get("Amount"),
            PartyA=validated_data.get("PhoneNumber"),
            PartyB=174379,
            PhoneNumber=validated_data.get("PhoneNumber"),
        )
        MpesaT.save()

        return MpesaT
