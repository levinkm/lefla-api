from tabnanny import check
from django.shortcuts import render
from rest_framework import generics, status
from django.utils import timezone
from rest_framework.response import Response
from .tasks import payUsingStkPush
import base64
from .utils import (
    mpesa_express,
    timestamp,
    mpesa_password,
    gerate_auth,
    mpesaExpressQuery,
)
from .serializers import MpesaSerializer
from .utils import mpesa_express
from bookings.models import Bookings, Checkout
from bookings.serializers import CheckoutSerializer
from .models import UnconfirmedMpesaStkPush
import http.client
import json

conn = http.client.HTTPSConnection("sandbox.safaricom.co.ke")


class mpesaExpressView(generics.GenericAPIView):
    http_method_names = ["post"]
    serializer_class = MpesaSerializer

    def post(self, request, *args, **kwargs):
        try:
            request_body = request.data
            p = timestamp()
            # print('Timestamp:',mpesa_password())

            g = gerate_auth()
            # vi = {"Authorization": "Bearer %s" % g}
            headers = {
                "Authorization": "Bearer %s" % g,
                # 'Content-Type': 'application/json'
            }
            booking = Bookings.objects.get(booking_id=request_body["booking"])
            # amount = booking.hostel.deposit

            # if booking.status == "ACCEPTED":

            if booking.status == "BOOKED":
                raise ValueError("Already Booked a visit")
            else:
                userPhoneNumber = booking.tenant.phonenumber
                if "+" in str(userPhoneNumber):
                    print(str(userPhoneNumber)[1:])
                else:
                    print(userPhoneNumber)

                payload = {
                    "BusinessShortCode": 174379,
                    "Password": mpesa_password(),
                    "Timestamp": timestamp(),
                    "TransactionType": "CustomerPayBillOnline",
                    "Amount": request_body["Amount"],
                    "PartyA": request_body["PhoneNumber"],
                    "PartyB": 174379,
                    "PhoneNumber": request_body["PhoneNumber"],
                    "CallBackURL": "https://dd60-197-232-61-218.in.ngrok.io",
                    "AccountReference": "Lefla Accomodations",
                    "TransactionDesc": "Payment of X",
                }
                booking = request_body["booking"]
                amount = request_body["Amount"]

                payUsingStkPush.delay(headers, payload, booking, amount)

                context = {
                    "message": "Booking request Successfull please accept stkpush sent",
                    "status": status.HTTP_200_OK,
                }
                return Response(context, status=status.HTTP_200_OK)
        except Exception as err:
            context = {
                "error": str(err),
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# {
#     "MerchantRequestID": "12895-51011014-1",
#     "CheckoutRequestID": "ws_CO_02102022204709911768850685",
#     "ResponseCode": "0",
#     "ResponseDescription": "Success. Request accepted for processing",
#     "CustomerMessage": "Success. Request accepted for processing"
# }


# {
#   "ResponseCode": "0",
#   "ResponseDescription": "The service request has been accepted successsfully",
#   "MerchantRequestID": "12895-51011014-1",
#   "CheckoutRequestID": "ws_CO_02102022204709911768850685",
#   "ResultCode": "0",
#   "ResultDesc": "The service request is processed successfully."
# }
