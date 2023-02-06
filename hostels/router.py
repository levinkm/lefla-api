from rest_framework import routers
from .views import HostelListAPIViewset, RoomListAPIViewset

hostels = routers.DefaultRouter()
hostels.register("hostels", HostelListAPIViewset, basename="Hostels")

rooms = routers.DefaultRouter()
rooms.register("rooms", RoomListAPIViewset, basename="Rooms")
