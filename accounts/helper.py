from django.conf import settings
from twilio.rest import Client
from django.core.mail import EmailMessage

class MessageHandler:

    phone_number = None
    otp = None

    def __init__(self,phone_number, otp) -> None:
        self.phone_number = phone_number
        self.otp = otp

    def send_otp(self):
        account = settings.Twillo_SID
        token = settings.Twillo_Token
        client = Client(account, token)

        message = client.messages.create(to=self.phone_number, from_= settings.Twillo_Phonenumber,
                                body=f'Jambo Welcome to Lefla. Here is your OTP: {self.otp}')



class EmailHandler:

    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject= data['email_sub'],
            body= data['email_body'],
            to = [data['to_email']]
        )
