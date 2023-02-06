from celery import shared_task
from .utils import mpesa_express, mpesaExpressQuery
from .utils import mpesaExpressQuery
from time import sleep
from bookings.models import Bookings, Checkout
from hostels.models import Virtual_Wallet
from .models import UnconfirmedMpesaStkPush


import time


@shared_task(name="Mpesa_check")
def checkMpesa(instance, created, **kwargs):
    sleep(50)
    if created:
        res = mpesaExpressQuery(instance.CheckoutRequestID)
        if res["ResultCode"] == "0":
            instance.is_confirmed = True
            instance.status = "PAID"
            instance.save()
            if instance.booking:

                if instance.booking.status == "ACCEPTED":
                    instance.booking.status = "VISITED"
                    instance.booking.save()
                elif instance.booking.status == "VISITED":
                    instance.booking.status = "BOOKED"
                    instance.booking.save()

                Checkout.objects.create(
                    booking=instance.booking,
                    amount_paid=instance.amount,
                    is_paid=True,
                )

                vw = Virtual_Wallet.objects.get(user=instance.booking.tenant)

                vw.available_amount = float(vw.available_amount) + float(
                    instance.amount
                )
                vw.save()

        else:
            if instance.booking:
                instance.booking.reason_for_cancelling = (
                    "Cancelled STK push/insufficient funds"
                )
                instance.booking.save()

            instance.is_confirmed = True

            instance.status = "CANCELLED"
            instance.save()


@shared_task(name="Mpesa_check")
def checkStkMpesa(CheckouId, Amount, walletID, **kwargs):

    res = mpesaExpressQuery(CheckouId)
    if res["ResultCode"] == "0":
        print(walletID)

        vw = Virtual_Wallet.objects.get(wallet_id=walletID)
        print(vw.available_amount)
        vw.available_amount = float(vw.available_amount) + float(Amount)
        vw.save()
        print(vw.available_amount)


@shared_task(name="pay_by_mpesa")
def payUsingStkPush(headers, payload, booking, amount):
    a = mpesa_express(headers=headers, payload=payload)
    mpesa_res = a.json()

    UnconfirmedMpesaStkPush.objects.create(
        booking=Bookings.objects.get(booking_id=booking),
        MerchantRequestID=mpesa_res["MerchantRequestID"],
        CheckoutRequestID=mpesa_res["CheckoutRequestID"],
        ResponseDescription=mpesa_res["ResponseDescription"],
        CustomerMessage=mpesa_res["CustomerMessage"],
        ResponseCode=mpesa_res["ResponseCode"],
        amount=amount,
    )


@shared_task(name="wallet_topup")
def WalletTopUp(headers, payload, walletID, amount):
    a = mpesa_express(headers=headers, payload=payload)
    mpesa_res = a.json()
    stkpush = UnconfirmedMpesaStkPush.objects.create(
        MerchantRequestID=mpesa_res["MerchantRequestID"],
        CheckoutRequestID=mpesa_res["CheckoutRequestID"],
        ResponseDescription=mpesa_res["ResponseDescription"],
        CustomerMessage=mpesa_res["CustomerMessage"],
        ResponseCode=mpesa_res["ResponseCode"],
        amount=amount,
    )
    vw = Virtual_Wallet.objects.get(wallet_id=walletID)
    print(vw.available_amount)
    vw.available_amount = float(vw.available_amount) + float(amount)
    vw.save()
    # sleep(50)
    # checkStkMpesa.delay(mpesa_res["CheckoutRequestID"], amount, walletID)
