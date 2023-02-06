from django.urls import re_path
from .consumers import BookingNotificationConsumer, ChatConsumer

websocket_urlpatterns = [
    re_path(
        r"ws/landlord-notifs/(?P<room_name>\w+)/$",
        BookingNotificationConsumer.as_asgi(),
    )
]
