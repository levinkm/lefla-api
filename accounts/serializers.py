from dataclasses import fields
import email
import phonenumbers
from rest_framework.exceptions import ValidationError
import random
from rest_framework import serializers
from rest_framework.serializers import CharField, ModelSerializer
from .models import Accounts
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.utils.encoding import (
    smart_str,
    force_str,
    smart_bytes,
    DjangoUnicodeDecodeError,
)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.exceptions import AuthenticationFailed
from hostels.models import Virtual_Wallet
from django.core.mail import EmailMessage

from .helper import EmailHandler


class RegisterSerializer(ModelSerializer):
    password_confirmation = CharField(required=False, write_only=True)
    password = CharField(max_length=65, min_length=8, write_only=True)

    class Meta:
        model = Accounts
        fields = (
            "email",
            "username",
            "phonenumber",
            "password",
            "password_confirmation",
            "fullname",
            "picture",
        )

    def validate(self, data):
        if data["password"] != data["password_confirmation"]:
            raise ValidationError({"error_message": "Passwords do not match"})
        if (
            data["username"].upper() == "ADMIN"
            or data["username"].upper() == "SUPERADMIN"
            or data["username"].upper() == "USER"
            or data["username"].upper() == "SUPERUSER"
        ):
            raise ValidationError({"error_message": "Kindly choose another username"})
        return data

    def create(self, validated_data):
        user = Accounts.objects.create(
            email=validated_data.get("email"),
            username=validated_data.get("username"),
            phonenumber=validated_data.get("phonenumber"),
            password=validated_data.get("password"),
            parent_phonenumber=validated_data.get("parent_phonenumber"),
        )
        user.is_active = False
        user.set_password(validated_data.get("password"))
        user.save()

        return user


class PasswordConfirmation(serializers.ModelSerializer):
    uidb64 = serializers.CharField(max_length=3)
    token = serializers.CharField(max_length=45)

    class Meta:
        model = Accounts
        fields = ("uidb64", "token", "password")


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ["email"]


class VerificationSerializer(serializers.Serializer):
    class Meta:
        fields = [""]


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8, max_length=64, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ["password", "token", "uidb64"]

    def validate(self, attrs):
        try:
            password = attrs.get("password")
            token = attrs.get("token")
            uidb64 = attrs.get("uidb64")

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator.check_token(user, token):
                raise AuthenticationFailed("The reset link is invalid", 401)

            user.set_password(password)
            user.save()
        except Exception as e:
            raise AuthenticationFailed("The reset link is invalid", 401)
        return super().validate(attrs)


class UserSeializer(serializers.ModelSerializer):
    class Meta:
        model = Accounts
        fields = (
            "email",
            "username",
            "phonenumber",
            "fullname",
            "picture",
            "date_joined",
            "is_landlord",
        )
