from django.urls import path, include, re_path
from .views import (
    BookingListViewset,
    BookingViewset,
    BookingAcceptView,
    RequestedVisitsView,
    RentalBookingViewset,
)

urlpatterns = [
    path("book-hostel-visit", BookingViewset.as_view(), name="Booking-hostel"),
    path(
        "book-hostel/<booking_id>",
        RentalBookingViewset.as_view(),
        name="Booking-hostel",
    ),
    path(
        "list-bookings/<user_id>",
        BookingListViewset.as_view(),
        name="user-bookings",
    ),
    path(
        "booking-status", BookingAcceptView.as_view(), name="accept-booking-by-landlord"
    ),
    path(
        "requested-bookings/<int:landlord_id>",
        RequestedVisitsView.as_view(),
        name="requested-bookings-landlord",
    ),
]
