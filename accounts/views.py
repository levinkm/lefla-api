from ast import arg
from email import message
from multiprocessing.sharedctypes import Value
from webbrowser import get
from django.shortcuts import render
from django.views import View
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    RegisterSerializer,
    ResetPasswordSerializer,
    VerificationSerializer,
    SetNewPasswordSerializer,
    PasswordConfirmation,
    UserSeializer,
)
from .helper import EmailHandler
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

# from django.contrib.auth.models import User
from django.shortcuts import redirect
from .utils import token_gen
from django.utils.encoding import (
    force_bytes,
    smart_str,
    force_str,
    smart_bytes,
    DjangoUnicodeDecodeError,
)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from .models import Accounts
from django.utils.encoding import force_str

force_text = force_str

from django.urls import reverse
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site


class PasswordConfirmView(generics.ListCreateAPIView):
    """
    Enables reset of a new password
    """

    http_method_names = ["post", "head", "options"]

    serializer_class = PasswordConfirmation

    def get_queryset(self):
        pass

    def post(self, request, *args, **kwargs):
        print(request.data)
        uidu = request.data["uidb64"]
        token = request.data["token"]
        password = request.data["password"]

        id1 = smart_str(urlsafe_base64_decode(uidu))
        print(id1, "This is the id")
        user = Accounts.objects.get(id=id1)

        if not PasswordResetTokenGenerator().check_token(user=user, token=token):

            return Response(
                {
                    "success": False,
                    "Error": "Token Not valid, Please request another one",
                    "status": status.HTTP_401_UNAUTHORIZED,
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        else:
            try:
                if password == "" or len(password) < 8:
                    return Response(
                        {
                            "success": False,
                            "Error": "password must have atleast 8 characters",
                            "status": status.HTTP_401_UNAUTHORIZED,
                        },
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
                else:
                    user.set_password(password)
                    user.save()
                    print(user, "done")
                    return Response(
                        {
                            "success": True,
                            "Message": "Password Changed Succesfuly",
                            "status": status.HTTP_200_OK,
                        },
                        status=status.HTTP_200_OK,
                    )
            except:
                return Response(
                    {
                        "success": False,
                        "Error": "password must have atleast 8 characters",
                        "status": status.HTTP_401_UNAUTHORIZED,
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )


class register(generics.CreateAPIView):
    """
    Enables registration of a new user returning the keyed in details if successful
    """

    queryset = Accounts.objects.all()
    serializer_class = RegisterSerializer

    def post(self, request):
        # print(request)
        data = request.data
        serializer = RegisterSerializer(data=data)

        # user.is_active= False
        # user.set_password(serializer.validated_data.get('password'))
        # user.save()
        if serializer.is_valid():
            user = Accounts.objects.create(
                email=serializer.validated_data.get("email"),
                username=serializer.validated_data.get("username"),
                phonenumber=serializer.validated_data.get("phonenumber"),
                password=serializer.validated_data.get("password"),
                # fullname =  serializer.validated_data.get('fullname'),
                parent_phonenumber=serializer.validated_data.get("parent_phonenumber"),
            )
            user.is_active = False
            user.set_password(user.password)
            user.save()

            # path to the view
            # get dormain we are on
            # relative url to verification
            # encode uid
            # token
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            # token =

            dormain = get_current_site(request).domain
            link = reverse(
                "activate",
                kwargs={"uidb64": uidb64, "token": token_gen.make_token(user)},
            )
            activate_url = "http://" + dormain + link
            email_sub = "Lefla Acount Activation"
            email_body = (
                "Hi "
                + serializer.validated_data.get("username")
                + "\n"
                + "Welcome to Lefla Accomodations. Use this link to verify and activate your account\n"
                + activate_url
            )
            email = EmailMessage(
                email_sub,
                email_body,
                "noreply@lefla.com",
                [serializer.validated_data.get("email")],
                # reply_to=['another@example.com']
                # headers={'Message-ID': 'foo'},
            )
            email.send(fail_silently=False)

            return Response(
                {
                    "results": serializer.data,
                    "status": status.HTTP_201_CREATED,
                    "success": True,
                },
                status=status.HTTP_201_CREATED,
            )
        elif Accounts.objects.filter(email=serializer.validated_data.get("email")):
            return Response(
                {
                    "error": "email already taken",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "success": False,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif Accounts.objects.filter(
            username=serializer.validated_data.get("username")
        ):
            return Response(
                {
                    "error": "username already taken",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "success": False,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        elif Accounts.objects.filter(
            username=serializer.validated_data.get("username"),
            email=serializer.validated_data.get("email"),
        ):
            return Response(
                {
                    "error": "username already taken",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "success": False,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return Response(
                {
                    "error": serializer.errors,
                    "status": status.HTTP_400_BAD_REQUEST,
                    "success": False,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class RequestPasswordReset(generics.GenericAPIView):
    """
    Handles reset password request and sends the reset link to the provided email provided if exist in the database
    """

    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        # serializer.is_valid(raise_exception=True)
        email = request.data["email"]
        if Accounts.objects.filter(email=email).exists():
            user = Accounts.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            # dormain = get_current_site(request).domain
            # dormain = 'lefla.vercel.app/auth/set-password/'
            link = reverse(
                "password_reset_confirm", kwargs={"uidb64": uidb64, "token": token}
            )
            activate_url = f"http://lefla.vercel.app/auth/set-password/?uidb64={uidb64}&token={token}"
            print(activate_url)
            email_sub = "LeFla Password Reset"
            email_body = (
                "Hello,"
                + "\n"
                + "We have received a password reset request from your email. Use this link to reset password\n"
                + activate_url
            )

            # data = {
            #     'email_body' : email_body,
            #     'to_email': user.email,
            #     'email_sub': email_sub,
            # }

            email = EmailMessage(
                email_sub,
                email_body,
                "noreply@lefla.com",
                [user.email],
            )
            email.send(fail_silently=False)

            return Response(
                {
                    "success": True,
                    "message": "Password reset Link has been sent to your email",
                },
                status=status.HTTP_200_OK,
            )

        else:
            return Response(
                {
                    "success": False,
                    "message": "not found",
                },
                status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
            )


class ValidateOtp(generics.GenericAPIView):
    """
    If the user receives the otp and sends it back the, this class will validate it and check wheather it is a match or not
    """

    def post(self, request):
        otp = request.data


class PasswordTokenCheck(generics.GenericAPIView):
    """
    Handles password Reset sent to the provided email
    """

    serializer_class = VerificationSerializer

    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = Accounts.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user=user, token=token):
                return Response(
                    {"Error": "Token Not valid, Please request another one"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            return (
                Response(
                    {
                        "success": True,
                        "Message": "Creds Valid",
                        "uidb64": uidb64,
                        "token": token,
                    },
                    status=status.HTTP_200_OK,
                ),
            )

        except DjangoUnicodeDecodeError as ex:
            if not PasswordResetTokenGenerator.check_token(user):
                return Response(
                    {"Error": "Token Not valid, Please request another one"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )


class SetNewPassword(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exceptions=True)
        return Response(
            {"success": True, "message": "Password Reset success"},
            status=status.HTTP_200_OK,
        )


class VerificationView(generics.ListAPIView):
    """
    used to activate the user account using link sent to the email. When the user clicks on the link sent them , this end point will check to see if it's authentic before redirecticting the user to the login page of the website if legit.
    """

    serializer_class = VerificationSerializer

    def get(self, request, uidb64, token):

        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = Accounts.objects.get(pk=id)

            if user.is_active:
                return redirect(
                    "http://lefla.vercel.app/auth/verify-account/?verified=true"
                )  # will replace with the link to the web version of the app

            user.is_active = True
            user.save()
            return redirect(
                "http://lefla.vercel.app/auth/verify-account/?verified=true"
            )  # will replace with the link to the web version of the app
        except Exception as ex:
            return Response(
                {
                    "success": False,
                    "message": str(e) if str(e) else "Please request another Link",
                },
                status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
            )


class UserView(generics.ListAPIView):
    serializer_class = UserSeializer

    def get_queryset(self):
        pass

    def get(self, request, *args, **kwargs):
        params = kwargs
        try:
            res = Accounts.objects.get(id=params["user_id"])
            serializer = self.serializer_class(res)
            context = {"data": serializer.data, "status": status.HTTP_200_OK}
            return Response(context, status=status.HTTP_200_OK)
        except Accounts.DoesNotExist:
            context = {
                "error": "Account does not exist",
                "status": status.HTTP_404_NOT_FOUND,
            }
            return Response(context, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            context = {
                "error": str(err),
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
