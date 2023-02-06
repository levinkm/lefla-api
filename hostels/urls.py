from unicodedata import name
from django.urls import URLPattern, path, include, re_path
from .views import (
    CategoryHostelView,
    ListLandlords,
    HostelCreateViewSet,
    RoomListAPIViewset,
    SearchRoomsView,
    TopUpWallet,
    IsLandlordView,
    ViertualWallet,
)
from .router import hostels, rooms
from django.contrib.auth import views

urlpatterns = [
    # landlord
    path("landlords", ListLandlords.as_view()),
    path("is_landlord/<user_id>", IsLandlordView.as_view()),
    # hostel
    path("hostels-cat/<category>", CategoryHostelView.as_view()),
    path("", include(hostels.urls)),
    # path("", include(rooms.urls)),
    path("rooms/", RoomListAPIViewset.as_view({"get": "list"})),
    path("add-hostel", HostelCreateViewSet.as_view()),
    path("search-rooms", SearchRoomsView.as_view()),
    # Wallet
    path("top-up-wallet", TopUpWallet.as_view()),
    path("wallet/<user_id>", ViertualWallet.as_view()),
]
