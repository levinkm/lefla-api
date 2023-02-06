from django.urls import path,include,re_path
from .views import (
    mpesaExpressView
)

urlpatterns = [
    path('transactions/callback', mpesaExpressView.as_view()), # TOD./mO: uncomment this after the mpesa endpoint works


]