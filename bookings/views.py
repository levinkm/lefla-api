from urllib.request import Request
from django.shortcuts import render
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from accounts.models import Accounts
from hostels.models import Hostel, Room, Virtual_Wallet
from django.http import JsonResponse
from django.db.models import Q, F
from Transactions.utils import (
    VirtualWalletTransact,
    gerate_auth,
    mpesa_password,
    timestamp,
)
from Transactions.tasks import mpesa_express, payUsingStkPush
from bookings.models import Bookings, Checkout
from .serializers import (
    BookingSerializer,
    BookingPostSerializer,
    CheckoutSerializer,
    DamagePenaltySerializer,
    BookingAcceptanceSerializer,
    VisitRequestSerializer,
    BookHostelSerializer,
)
from Transactions.payments.stkpush import stkPushRequest
from Transactions.payments.mpesavariables import *


# Create your views here.


class RentalBookingViewset(generics.CreateAPIView):
    """used to book hostels after paying a visit"""

    serializer_class = BookingPostSerializer
    http_method_names = ["post", "head"]

    def post(self, request, *args, **kwargs):
        request_body = request.data

        params = kwargs
        try:

            booking_id = params["booking_id"]

            check = Bookings.objects.get(
                Q(booking_id=booking_id),
            )

            if check:
                tenant = check.tenant
                landlord = check.room.hostel_id.landlord.user
                landlordvw = Virtual_Wallet.objects.get(user=landlord)
                tenantvw = Virtual_Wallet.objects.get(user=tenant)

                if tenantvw.available_amount >= check.room.total_amount:
                    res = VirtualWalletTransact(
                        tenantvw.wallet_id,
                        landlordvw.wallet_id,
                        check.room.total_amount,
                    )
                    print(res)
                    if res["success"]:
                        check.status = "BOOKED"
                        check.save()
                        Room.objects.filter(id=check.room).update(
                            number_of_rooms_avilable=F("number_of_rooms_avilable") - 1
                        )
                        context = {
                            "message": "Booking placed successful",
                            "status": status.HTTP_200_OK,
                        }
                        return Response(context, status=status.HTTP_200_OK)
                else:
                    try:
                        g = gerate_auth()
                        headers = {
                            "Authorization": "Bearer %s" % g,
                        }
                        payload = {
                            "BusinessShortCode": 174379,
                            "Password": mpesa_password(),
                            "Timestamp": timestamp(),
                            "TransactionType": "CustomerPayBillOnline",
                            "Amount": float(check.room.total_amount),
                            "PartyA": request_body["PhoneNumber"],
                            "PartyB": 174379,
                            "PhoneNumber": request_body["PhoneNumber"],
                            "CallBackURL": "https://dd60-197-232-61-218.in.ngrok.io",
                            "AccountReference": "Lefla Accomodations",
                            "TransactionDesc": "Payment of X",
                        }
                        booking = check.booking_id
                        amount = float(check.room.total_amount)

                        payUsingStkPush.delay(headers, payload, booking, amount)

                        context = {
                            "message": "Booking request is being processed ",
                            "status": status.HTTP_200_OK,
                        }
                        return Response(context, status=status.HTTP_200_OK)
                    except Exception as err:
                        context = {
                            "error": str(err) + " error 1",
                            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                        }
                        return Response(
                            context, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )

            else:
                raise ValueError("You've already booked this room")
        except Exception as err:
            context = {
                "error": str(err) + " error 2",
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BookingViewset(generics.CreateAPIView):
    """
    Used to make a booking . you will have to pass both hostel id and the potential tenant id (user_id) as the tenant id
    """

    serializer_class = BookHostelSerializer
    queryset = Bookings.objects.all()
    http_method_names = ["post", "head"]

    def post(self, request, *args, **kwargs):
        request_body = request.data
        try:

            tenant_id = request_body["tenant"]
            # hostel_id = request_body["room"]
            check = Bookings.objects.filter(
                Q(tenant=tenant_id),
                Q(room=request_body["room"]),
                Q(status="BOOKED") | Q(status="ACCEPTED") | Q(status="REQUESTED"),
            )

            if check:
                raise ValueError("You've already booked this hostel")
            else:

                booking = Bookings.objects.create(
                    tenant=Accounts.objects.get(id=tenant_id),
                    room=Room.objects.get(id=request_body["room"]),
                )
                booking.save()
                Room.objects.filter(id=request_body["room"]).update(
                    number_of_rooms_avilable=F("number_of_rooms_avilable") - 1
                )

            context = {
                "message": "Booking placed successful",
                "status": status.HTTP_201_CREATED,
            }
            return Response(context, status=status.HTTP_201_CREATED)
        except Exception as err:
            context = {
                "error": str(err),
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BookingListViewset(generics.CreateAPIView):
    """
    Used to list all the bookings made by the user.
    """

    serializer_class = BookingSerializer
    http_method_names = ["get", "head"]
    lookup_field = "tenant"

    def get(self, request, *args, **kwargs):
        params = kwargs
        try:
            data = Bookings.objects.filter(tenant=params["user_id"])
            serializer = BookingSerializer(
                data, context={"request": request}, many=True
            )

            if serializer:
                context = {
                    "data": serializer.data,
                    "status": status.HTTP_200_OK,
                }
            else:
                raise ValueError("No bookings made")

            return Response(context, status=status.HTTP_200_OK)
        except Exception as err:
            context = {
                "error": str(err),
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BookingAcceptView(generics.UpdateAPIView):
    """
    This endpoint takes three parameters as shown below. The status Parameter should have one of the foollowing Five options.(REQUESTED,ACCEPTED,BOOKED,COMPLETED,CANCELLED). This status option is what will be used to track the booking progress
    """

    http_method_names = ["put"]
    serializer_class = BookingAcceptanceSerializer

    def put(self, request, *args, **kwargs):
        request_body = request.data
        try:
            Bookings.objects.filter(booking_id=request_body["booking_id"]).update(
                status=request_body["status"],
                reason_for_cancelling=request_body["reason_for_cancelling"]
                if request_body["reason_for_cancelling"]
                else "",
            )
            context = {
                "message": "Booking status updated",
                "status": status.HTTP_200_OK,
            }
            return Response(context, status=status.HTTP_200_OK)
        except Exception as err:
            context = {
                "error": str(err),
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# TODO: Add shared tasks for emailing the user whenever the landlord accepts the booking and also emailing the landlord
# when there is a new booking placed.


class CheckoutView(generics.CreateAPIView):
    """
    here is where bookings are paid for( most probaly the deposit first ).
    """

    serializer_class = CheckoutSerializer
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        try:
            request_body = request.data
            checkout = Checkout.objects.create(
                booking=request_body["booking"],
                amount_paid=request_body["amount_paid"],
                is_paid=True,
            )

            stkPushRequest()

            context = {
                "message": "Checkout Successfull",
                "status": status.HTTP_200_OK,
            }
            return Response(context, status=status.HTTP_200_OK)
        except Exception as err:
            context = {
                "error": str(err),
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# TODO: create a logic for Damage penalty and to be able to deduct from deposit.


class RequestedVisitsView(generics.ListAPIView):
    """
    used to check all the new requested visits made by interested tenants
    """

    http_method_names = ["get", "head", "options"]

    serializer_class = VisitRequestSerializer

    def get(self, request, *args, **kwargs):
        params = kwargs
        landlord = params["landlord_id"]
        print(params)
        try:
            queryset = Bookings.objects.filter(
                room__hostel_id__landlord=landlord, status="REQUESTED"
            )
            serializer = self.serializer_class(queryset, many=True)
            context = {"requests": serializer.data, "status": status.HTTP_200_OK}
            return Response(context, status=status.HTTP_200_OK)
        except Exception as err:
            context = {
                "error": str(err),
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
