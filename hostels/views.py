from importlib.metadata import files
from urllib.robotparser import RequestRate
from django.shortcuts import render
from django.db.models import Q
from rest_framework import generics, viewsets, pagination, status
from rest_framework.response import Response

from Transactions.tasks import WalletTopUp
from Transactions.utils import mpesa_password, timestamp, gerate_auth
from .models import Hostel, RoomImages, Virtual_Wallet, Landlord, Category, Room
from .serializers import (
    Hostelerializer,
    LandLordSerializer,
    HostelAddSerializer,
    TopUpWalletSerializer,
    Virtual_Wallet,
    HostelSearcherializer,
    RoomSerializer,
    WalletSerializer,
    RoomSerializerDetailed,
)

from .pillowutils import compress_img
from PIL import Image
from .utils import compressImageSave

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers


class LargeResultsSetPagination(pagination.PageNumberPagination):
    """Class for Custom Pagination"""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000


class CategoryHostelView(generics.ListAPIView):
    """
    Used to filter hostels based on the categories
    """

    http_method_names = ["get", "head", "options"]
    pagination_class = LargeResultsSetPagination
    serializer_class = Hostelerializer
    queryset = Hostel.objects.all()
    lookup_field = "category"

    def get_queryset(self, *args, **kwargs):
        specific_hotels = Hostel.objects.all()
        return specific_hotels

    def get(self, request, *args, **kwargs):
        params = kwargs
        print(params)
        specific_hotels = Hostel.objects.filter(category=params["category"])
        try:
            data = Hostelerializer(specific_hotels, many=True).data
            assert data
            context = {"data": data, "success": True, "status": status.HTTP_200_OK}
            return Response(context, content_type="json")
        except Exception as err:
            context = {
                "error": str(err) if str(err) else "Hostel not found",
                "success": "false",
                "messages": "Failed To Get Hostels.",
            }
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HostelCreateViewSet(generics.CreateAPIView):
    """
    this endpoint is used in adding hostels/rentals to the system. This is done by landlords after being registered\n
    Below is the skeleton request body that is ti be used\n


    """

    queryset = Hostel.objects.all()
    serializer_class = HostelAddSerializer
    permission_classes = []


class HostelListAPIViewset(viewsets.ModelViewSet):
    """
    Used to get specific hostels from the db. You can add page size or page number as parameters for pagination.d
    """

    queryset = Hostel.objects.all()
    serializer_class = Hostelerializer
    # pagination_class = LargeResultsSetPagination
    http_method_names = ["get", "options", "head"]
    lookup_field = "id"

    def get_queryset(self):
        specific_job = Hostel.objects.filter()

        return specific_job

    def retrieve(self, request, *args, **kwargs):
        params = kwargs
        data = Hostel.objects.filter(id=int(params["id"]))
        seralizer = Hostelerializer(data, many=True)
        context = {
            "data": seralizer.data,
            "success": True,
            "status": status.HTTP_200_OK,
        }
        return Response(
            {
                "results": seralizer.data,
                "success": True if seralizer.data else False,
                "status": status.HTTP_200_OK
                if seralizer.data
                else status.HTTP_404_NOT_FOUND,
            }
        )


class RoomListAPIViewset(viewsets.ModelViewSet):
    """
    Used to get rooms from the db. You can add page size or page number as parameters for pagination.d
    """

    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    pagination_class = LargeResultsSetPagination
    http_method_names = ["get", "options", "head"]
    lookup_field = "id"

    # @method_decorator(cache_page(60 * 60 * 2))
    # @method_decorator(
    #     vary_on_headers(
    #         "Authorization",
    #     )
    # )
    # def get_queryset(self):

    #     specific_job = Room.objects.filter(number_of_rooms_avilable__gte=1)

    #     return specific_job

    @method_decorator(cache_page(60 * 60 * 2))
    @method_decorator(
        vary_on_headers(
            "Authorization",
        )
    )
    def list(self, request, *args, **kwargs):
        detailed = (
            request.GET.get("detailed") if request.GET.get("detailed") else "False"
        )

        if str(detailed.upper()) == "TRUE":
            specific_job = Room.objects.filter(is_booked=False)
            serializer = RoomSerializerDetailed(specific_job, many=True)
            context = {
                "data": serializer.data,
                "success": True,
                "status": status.HTTP_200_OK,
            }
            return Response(context, status=status.HTTP_200_OK)

        else:

            specific_job = Room.objects.filter(is_booked=False)
            serializer = self.serializer_class(specific_job, many=True)
            context = {
                "data": serializer.data,
                "success": True,
                "status": status.HTTP_200_OK,
            }
            return Response(context, status=status.HTTP_200_OK)

    @method_decorator(cache_page(60 * 20))
    @method_decorator(
        vary_on_headers(
            "Authorization",
        )
    )
    def retrieve(self, request, *args, **kwargs):
        params = kwargs
        data = Room.objects.filter(id=params["id"])
        seralizer = RoomSerializerDetailed(data, many=True)
        context = {
            "data": seralizer.data,
            "success": True,
            "status": status.HTTP_200_OK,
        }
        return Response(
            {
                "results": seralizer.data,
                "success": True if seralizer.data else False,
                "status": status.HTTP_200_OK
                if seralizer.data
                else status.HTTP_404_NOT_FOUND,
            }
        )


class SearchRoomsView(generics.ListAPIView):
    """
    use this endpoint for search.
    """

    queryset = Room.objects.all()
    serializer_class = RoomSerializer  # /Hostelerializer
    pagination_class = LargeResultsSetPagination
    http_method_names = ["get", "options", "head"]
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        request_body = request.data
        try:
            if request_body["hostel_name"]:
                data = Room.objects.filter(
                    hostel_id__hostel_name__icontains=request_body["hostel_name"]
                )
            elif request_body["category"]:
                data = Room.objects.filter(room_type=request_body["category"]).filter(
                    Q(hostel_id__place_name__icontains=request_body["place_name"])
                    | Q(hostel_id__town__icontains=request_body["town"])
                    | Q(hostel_id__hostel_rating__gte=request_body["hostel_rating"])
                )
            elif request_body["town"]:
                data = (
                    Room.objects.filter(
                        hostel_id__town__icontains=request_body["town"]
                    ).filter(
                        Q(hostel_id__place_name__icontains=request_body["place_name"])
                        | Q(hostel_id__hostel_rating__gte=request_body["hostel_rating"])
                    )
                    if request_body["place_name"] or request_body["hostel_rating"]
                    else Room.objects.filter(
                        hostel_id__town__icontains=request_body["town"]
                    )
                )
            elif request_body["hostel_rating"] and request_body["place_name"]:
                data = Room.objects.filter(
                    Q(hostel_id__hostel_rating__gte=request_body["hostel_rating"]),
                    Q(hostel_id__place_name__icontains=request_body["place_name"]),
                )
            elif request_body["hostel_rating"]:
                data = Room.objects.filter(
                    Q(hostel_id__hostel_rating__gte=request_body["hostel_rating"]),
                )

            else:
                raise ValueError("No search parameter passed")

            serializer = self.serializer_class(
                data, context={"request": request}, many=True
            )
            return Response(
                {
                    "count": len(serializer.data),
                    "result": serializer.data,
                    "status": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as err:
            context = {
                "error": str(err) + "test 1",
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListLandlords(generics.ListAPIView):
    """
    used to list all the landlords in the system
    """

    queryset = Landlord
    serializer_class = LandLordSerializer

    def get_queryset(self):
        specific_hotels = Landlord.objects.all()
        return specific_hotels


class TopUpWallet(generics.ListAPIView):
    """
    used to deposit money on the wallet using wallet Id
    """

    http_method_names = ["post", "head", "options"]
    serializer_class = TopUpWalletSerializer

    def get_queryset(self):
        pass

    def post(self, request, *args, **kwargs):
        request_body = request.data

        try:
            g = gerate_auth()
            headers = {
                "Authorization": "Bearer %s" % g,
            }
            payload = {
                "BusinessShortCode": 174379,
                "Password": mpesa_password(),
                "Timestamp": timestamp(),
                "TransactionType": "CustomerPayBillOnline",
                "Amount": float(request_body["Amount"]),
                "PartyA": request_body["PhoneNumber"],
                "PartyB": 174379,
                "PhoneNumber": request_body["PhoneNumber"],
                "CallBackURL": "https://dd60-197-232-61-218.in.ngrok.io",
                "AccountReference": "Lefla Accomodations",
                "TransactionDesc": "Payment of X",
            }
            WalletTopUp.delay(
                headers,
                payload,
                request_body["wallet_id"],
                float(request_body["Amount"]),
            )
            return Response(
                {
                    "message": "Successful, Please Accespt the STK request sent",
                    "status": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as err:
            return Response(
                {"error": str(err), "status": status.HTTP_500_INTERNAL_SERVER_ERROR},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class IsLandlordView(generics.ListAPIView):
    islandlord = False

    def get(self, request, *args, **kwargs):
        params = kwargs

        try:
            data = Landlord.objects.get(user=params["user_id"])
            self.islandlord = True
        except Landlord.DoesNotExist:
            self.islandlord = False
        except Landlord.MultipleObjectsReturned:
            self.islandlord = True

        return Response(
            {"is_landlord": self.islandlord, "status": status.HTTP_200_OK},
            status=status.HTTP_200_OK,
        )


class ViertualWallet(generics.ListAPIView):

    serializer_class = WalletSerializer
    http_method_names = ["get", "head", "options"]

    def get_queryset(self):
        pass

    def get(self, request, *args, **kwargs):
        params = kwargs

        try:
            data = Virtual_Wallet.objects.get(user=params["user_id"])
            serializer = self.serializer_class(data)
            context = {"data": serializer.data, "status": status.HTTP_200_OK}
            return Response(context, status=status.HTTP_200_OK)
        except Virtual_Wallet.DoesNotExist:
            context = {
                "error": "No virtual wallet found",
                "status": status.HTTP_404_NOT_FOUND,
            }
            return Response(context, status=status.HTTP_404_NOT_FOUND)

        except Virtual_Wallet.MultipleObjectsReturned:
            context = {
                "error": "more than two wallets returned",
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as err:
            context = {
                "error": str(err),
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
            return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
