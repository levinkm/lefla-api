import requests
from datetime import datetime
from dateutil import parser as date_parser
from dateutil import tz
import base64, time

from .payments import mpesa as payment

from hostels.models import Virtual_Wallet


payment.SHORT_CODE = "174379"
payment.PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
payment.CONSUMER_SECRET = "ECcwy8RAJBPsfetM"
payment.CONSUMER_KEY = "BnZh5QNAPUuQwagJVIXHtSQKJRKaDXyg"
payment.ACCOUNT_TYPE = 174379  # Set to TILL to use BuyGoods instead of Pay Bill


def convert_timestamp_timezone(timestamp, from_tz="UTC", to_tz="UTC"):
    """
    function to convert a string timestamp between timezones
    @timestamp - A string timestamp (dateutil.parser will be used to parse)
    @from_tz - A string, the current timezone as a string.
    @to_tz - A string, the timezone to convert the time to.
    Refer to: http://goo.gl/hmPXML for a list of acceptable TZ strings
    """
    timestamp = date_parser.parse(timestamp)
    from_tz = tz.gettz(from_tz)
    to_tz = tz.gettz(to_tz)
    tz_aware_timestamp = timestamp.replace(tzinfo=from_tz)
    converted_timestamp = tz_aware_timestamp.astimezone(to_tz)
    return converted_timestamp


def timestamp():
    time_in_kenya = convert_timestamp_timezone(
        datetime.today().strftime("%Y-%m-%d %H:%M:%S"), "Africa/Nairobi", "UTC+3"
    )
    p = time_in_kenya.strftime("%Y%m%d%H%M%S")
    return p


def mpesa_express(headers, payload):

    saf_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    respo = requests.post(saf_url, headers=headers, json=payload)
    return respo


def mpesa_password():
    p = timestamp()
    l = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
    encoded = "174379" + l + p
    passwd = base64.b64encode(encoded.encode("ascii")).decode("utf-8")
    return passwd


def gerate_auth():
    encoded = "BnZh5QNAPUuQwagJVIXHtSQKJRKaDXyg" + "ECcwy8RAJBPsfetM"
    en = base64.b64encode(encoded.encode("ascii")).decode("utf-8")

    # headers = {
    #     # 'Authorization': 'Basic QXpzMktlalUxQVJ2SUw1SmRKc0FSYlYyZ0RyV21wT0I6aGlwR3ZGSmJPeHJpMzMwYw=='
    # }
    headers = {
        "Authorization": "Basic QXpzMktlalUxQVJ2SUw1SmRKc0FSYlYyZ0RyV21wT0I6aGlwR3ZGSmJPeHJpMzMwYw=="
    }

    response = requests.request(
        "GET",
        "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
        headers=headers,
    )

    return response.json()["access_token"]


def mpesaExpressQuery(checkoutId):
    g = gerate_auth()

    headers = {"Authorization": "Bearer %s" % g}

    payload = {
        "BusinessShortCode": 174379,
        "Password": mpesa_password(),
        "Timestamp": timestamp(),
        "CheckoutRequestID": checkoutId,
    }

    saf_express_query_url = (
        "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query"
    )

    response = requests.post(
        saf_express_query_url,
        headers=headers,
        json=payload,
    )
    return response.json()


# mpesaExpressQuery("ws_CO_02102022204709911768850685")


def queryStkRequest(
    checkout_request_id, business_shortcode=174379, timestamp=timestamp()
):
    password = mpesa_password()
    access_token = gerate_auth()
    headers = {
        "Authorization": "Bearer {0}".format(access_token),
        "Content-Type": "application/json",
    }
    payload = {
        "BusinessShortCode": business_shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "CheckoutRequestID": checkout_request_id,
    }

    # if ENV == "production":
    #     base_safaricom_url = LIVE_URL
    # else:
    #     base_safaricom_url = "https://sandbox.safaricom.co.ke"
    base_safaricom_url = "https://sandbox.safaricom.co.ke"

    saf_url = "{0}{1}".format(base_safaricom_url, "/mpesa/stkpushquery/v1/query")

    response = requests.post(saf_url, json=payload, headers=headers)

    if response.status_code != 200:
        print(f"!!! {response.reason} !!!")
        print(response.json())

    return response


def VirtualWalletTransact(sender_vw_id, receiver_vw_id, amount):
    try:

        sendervw = Virtual_Wallet.objects.get(wallet_id=sender_vw_id)
        receivervw = Virtual_Wallet.objects.get(wallet_id=receiver_vw_id)

        if sendervw.available_amount > amount:
            # deducting from sender
            sendervw.available_amount = float(sendervw.available_amount) - float(amount)
            # adding to receiver
            receivervw.available_amount = float(receivervw.available_amount) + float(
                amount
            )
            sendervw.save()
            receivervw.save()
            context = {"message": "money transacted successfuly", "success": True}
            return context
        else:
            raise ValueError("insufficient amount")

    except Exception as err:
        context = {"error": str(err), "success": False}
        return context
