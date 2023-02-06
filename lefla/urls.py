"""lefla URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.response import Response
from rest_framework import status
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer as TOKEN_OBTAIN_SERIALIZER,
)
from accounts.models import Accounts as acc
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenViewBase,
)
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.settings import api_settings

Accounts = settings.AUTH_USER_MODEL


class login(TokenViewBase):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            try:
                user = acc.objects.get(username=request.data["username"])
                if not user.is_active:
                    return Response(
                        {
                            "LoginError": "PLease check your email to activate your account",
                            "status": status.HTTP_401_UNAUTHORIZED,
                        },
                        status=status.HTTP_401_UNAUTHORIZED,
                        exception=True,
                    )
                else:
                    serializer.is_valid(raise_exception=True)
            except Exception as e:
                return Response(
                    {
                        "LoginError": "incorrect username or password",
                        "status": status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
                    },
                    status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
                    exception=True,
                )
        except TokenError as e:
            # raise InvalidToken(e.args[0])
            return Response(
                {
                    "LoginError": "incorrect password",
                    "status": status.HTTP_401_UNAUTHORIZED,
                },
                status=status.HTTP_401_UNAUTHORIZED,
                exception=True,
            )
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class tokenObtain(TOKEN_OBTAIN_SERIALIZER):
    default_error_messages = {
        "LoginError": "Incorect password,please check it and try again"
    }


class TokenObtainPairView(login):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """

    serializer_class = tokenObtain


urlpatterns = [
    path("admin/", admin.site.urls),
    path("debug/", include("debug_toolbar.urls")),
    path("api/", include("djoser.urls")),
    path("api/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/", include("accounts.urls")),
    path("api/", include("hostels.urls")),
    path("api/", include("Transactions.urls")),
    path("api/bookings/", include("bookings.urls")),
    path("api/docs/", include_docs_urls(title="LeFla Accomodations")),
    path(
        "",
        get_schema_view(
            title="LeFla Accomodations",
            description="Api for Lefla data",
            version="1.0.0",
        ),
        name="openapi-schema",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
