from unicodedata import name
from django.urls import URLPattern, path
from django.contrib.auth import views
from .views import (
    register,
    VerificationView,
    PasswordTokenCheck,
    RequestPasswordReset,
    SetNewPassword,
    PasswordConfirmView,
    UserView,
)

urlpatterns = [
    path("register/", register.as_view(), name="Register"),
    path("activate/<uidb64>/<token>/", VerificationView.as_view(), name="activate"),
    path(
        "password-reset/<uidb64>/<token>",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset-complete/",
        views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path(
        "request-reset-sent",
        views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path("reset-password", RequestPasswordReset.as_view(), name="request-reset-email"),
    path("set-password/", PasswordConfirmView.as_view(), name="set-newpassword"),
    path("account/<user_id>", UserView.as_view(), name="account-details"),
]
# path('/<uidb64>/<token>/', PasswordTokenCheck.as_view(), name = 'password-reset'),
# path('password-reset-complete', SetNewPassword.as_view() ,name = 'password-reset-complete'),
# path('password-reset/', auth_views.PasswordResetView.as_view(), name = 'reset_password'),
# path('password-reset-m/', RequestPasswordReset.as_view(), name = 'reset_password-m'),
# path('request-reset-sent',auth_views.PasswordResetDoneView.as_view(), name= 'password_reset_done'),
# path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view() ,name = 'password_reset_confirm'),
#
