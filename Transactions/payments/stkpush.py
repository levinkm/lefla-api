from urllib import response
from .mpesavariables import *
import requests
from requests.auth import HTTPBasicAuth
import base64
import datetime


def getAuthToken(app_key=STK_APP_KEY, app_secret=STK_APP_SECRET):

    if ENV == "production":
        base_safaricom_url = LIVE_URL
    else:
        base_safaricom_url = SANDBOX_URL

    authenticate_uri = "/oauth/v1/generate?grant_type=client_credentials"
    authenticate_url = "{0}{1}".format(base_safaricom_url, authenticate_uri)

    response = requests.get(authenticate_url, auth=HTTPBasicAuth(app_key, app_secret))

    if response.status_code == 200:
        access_token = response.json()["access_token"]
        expires_in = response.json()["expires_in"]
    else:
        print("!!! Error while getting access token !!!")
        print(response.reason)
        return "error"

    return access_token


def registerUrls(
    short_code,
    access_token,
    validation_url,
    confirmation_url,
):
    payload = {
        "ValidationURL": validation_url,
        "ConfirmationURL": confirmation_url,
        "ShortCode": short_code,
        "ResponseType": "Completed",
    }
    headers = {
        "Authorization": "Bearer {0}".format(access_token),
        "Content-Type": "application/json",
    }

    if ENV == "production":
        base_safaricom_url = LIVE_URL
    else:
        base_safaricom_url = SANDBOX_URL
    saf_url = "{0}{1}".format(base_safaricom_url, "/mpesa/c2b/v2/registerurl")
    response = requests.post(saf_url, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"!!! {response.reason} !!!")
        print(response.json())

    return response


def b2cRequest(
    initiator_name=B2C_INITIATOR_NAME,
    security_credential=SECURITY_CREDENTIAL,
    command_id="BusinessPayment",
    token=None,
    amount=None,
    party_a=B2C_SHORTCODE,
    party_b=None,
    remarks="Mpesa payment",
    queue_timeout_url=B2C_TIMEOUT,
    result_url=B2C_CALLBACK,
    occassion="",
):

    payload = {
        "InitiatorName": initiator_name,
        "SecurityCredential": security_credential,
        "CommandID": command_id,
        "Amount": amount,
        "PartyA": party_a,
        "PartyB": party_b,
        "Remarks": remarks,
        "QueueTimeOutURL": queue_timeout_url,
        "ResultURL": result_url,
        "Occassion": occassion,
    }
    headers = {
        "Authorization": "Bearer {0}".format(token),
        "Content-Type": "application/json",
    }
    if ENV == "production":
        base_safaricom_url = LIVE_URL
    else:
        base_safaricom_url = SANDBOX_URL
    saf_url = "{0}{1}".format(base_safaricom_url, "/mpesa/b2c/v1/paymentrequest")
    response = requests.post(saf_url, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"!!! {response.reason} !!!")
        print(response.json())

    return response


def generate_password(
    timestamp,
    business_shortcode=STK_SHORTCODE,
    passcode=PASSCODE,
):
    password_string = "{0}{1}{2}".format(
        str(business_shortcode), str(passcode), timestamp
    )
    # base64.b64encode() requires a byte string as a parameter so convert password string to a byte string
    # this returns base64 encoded password string
    encoded = base64.b64encode(password_string.encode())
    # the returned value is not serializable so we convert it back to utf-8
    return encoded.decode("utf-8")


def stkPushRequest(
    business_shortcode=STK_SHORTCODE,
    passcode=PASSCODE,
    callback_url=STK_PUSH_CALLBACK,
    description="Mpesa payment",
    access_token=None,
    amount=None,
    phone_number=None,
    reference_code=None,
    time_stamp=None,
):

    # time = str(datetime.datetime.now()).split(".")[0].replace("-", "").replace(" ", "").replace(":", "")

    password_string = "{0}{1}{2}".format(
        str(business_shortcode), str(passcode), time_stamp
    )
    # base64.b64encode() requires a byte string as a parameter so convert password string to a byte string
    # this returns base64 encoded password string
    encoded = base64.b64encode(password_string.encode())
    # the returned value is not serializable so we convert it back to utf-8
    serializable_password = encoded.decode("utf-8")

    payload = {
        "BusinessShortCode": business_shortcode,
        "Password": serializable_password,
        "Timestamp": time_stamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": int(phone_number),
        "PartyB": business_shortcode,
        "PhoneNumber": int(phone_number),
        "CallBackURL": callback_url,
        "AccountReference": reference_code,
        "TransactionDesc": description,
    }
    headers = {
        "Authorization": "Bearer {0}".format(access_token),
        "Content-Type": "application/json",
    }

    if ENV == "production":
        base_safaricom_url = LIVE_URL
    else:
        base_safaricom_url = SANDBOX_URL
    saf_url = "{0}{1}".format(base_safaricom_url, "/mpesa/stkpush/v1/processrequest")
    response = requests.post(saf_url, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"!!! {response.reason} !!!")
        print(response.json())

    return response


def queryStkRequest(
    password,
    timestamp,
    checkout_request_id,
    business_shortcode=STK_SHORTCODE,
):

    payload = {
        "BusinessShortCode": business_shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "CheckoutRequestID": checkout_request_id,
    }

    if ENV == "production":
        base_safaricom_url = LIVE_URL
    else:
        base_safaricom_url = SANDBOX_URL

    saf_url = "{0}{1}".format(base_safaricom_url, "/mpesa/stkpushquery/v1/query")

    response = requests.post(saf_url, json=payload)

    if response.status_code != 200:
        print(f"!!! {response.reason} !!!")
        print(response.json())

    return response
