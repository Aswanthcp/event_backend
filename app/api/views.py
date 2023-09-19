from rest_framework.generics import RetrieveUpdateAPIView
from django.db.models import Sum, F
from django.utils.timezone import timedelta
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_exempt
from .razorpay import create_order
import os
import razorpay
import json
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from rest_framework.decorators import api_view
import jwt
from ..models import *
from .serializer import *
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q

# admin view


def pagination(request, list_, type):
    page = request.GET.get("page", 1)
    paginator = Paginator(list_, 3)  # Number of items per page

    try:
        lists = paginator.page(page)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    if type == "user":
        serializer = MyUserSerializer(lists, many=True)
    elif type == "cord":
        serializer = CoordinatorSerializer(lists, many=True)
    elif type == "vender":
        serializer = VenderSerializer(lists, many=True)
    elif type == "category":
        serializer = CategorySerializer(lists, many=True)
    elif type == "eventType":
        serializer = EventTypeSerializer(lists, many=True)
    elif type == "event":
        serializer = EventSerializer(lists, many=True)
    elif type == "eventcoord":
        serializer = EventCoordinatorSerializer(lists, many=True)
    elif type == "eventorders":
        serializer = EventUserBookSerializer(lists, many=True)
    elif type == "itemsorders":
        serializer = ItemUserRentSerializer(lists, many=True)
    elif type == "items":
        serializer = ItemSerializer(lists, many=True)
    elif type == "eventyplelisting":
        serializer = EventTypeSerializerListing(lists, many=True)

    pagination_data = {
        "hasNextPage": lists.has_next(),
        "hasPrevPage": lists.has_previous(),
        "currentPage": lists.number,
        "totalPages": paginator.num_pages,
        "results": serializer.data,
    }

    return Response(pagination_data, status=status.HTTP_200_OK)


class AdminLogin(APIView):
    def post(self, request):
        data = request.data
        username = data["username"]
        password = data["password"]
        user = authenticate(username=username, password=password)
        serial = MyUserSerializer(user, many=False)
        if user is not None and user.is_superuser:
            payload = {
                "username": username,
                "email": user.email,
                "password": user.password,
            }
            jwt_token = jwt.encode(payload, "secret", algorithm="HS256")
            print(jwt_token)

            return Response({"data": serial.data, "admin_jwt": jwt_token})
        else:
            return Response("Invalid credentials")


@api_view(["GET"])
def getUsers(request):
    userslist = MyUser.objects.all().exclude(is_superuser=True)
    return pagination(request, userslist, "user")


@api_view(["GET", "PUT"])
def getUserbyId(request, id):
    userslist = MyUser.objects.get(id=id)
    if request.method == "GET":
        serializer = MyUserSerializer(userslist, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    if request.method == "PUT":
        serializer = MyUserSerializer(userslist, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )


@api_view(["GET", "POST"])
def getEvents(request):
    if request.method == "GET":
        event_list = Event.objects.all()
        # Assuming the pagination logic is defined elsewhere
        return pagination(request, event_list, "event")

    if request.method == "POST":
        id_ = request.data["type"]["id"]
        type_ = get_object_or_404(EventType, id=id_)
        request.data["type"] = type_.id
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(type=type_)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "POST"])
def getEventsall(request):
    if request.method == "GET":
        event_list = Event.objects.all()
        serializer = EventSerializer(event_list, many=True)
        return Response(serializer.data, status=201)


@api_view(["GET", "PUT", "DELETE"])
def getEventsbyID(request, id):
    event = Event.objects.get(id=id)
    if request.method == "GET":
        serializer = EventSerializer(event, many=False)
        return Response(serializer.data)
    if request.method == "PUT":
        serializer = EventSerializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )


@api_view(["GET"])
def getCordinators(request):
    cordinators = Coordinator.objects.all()
    return pagination(request, cordinators, "cord")


@api_view(["GET"])
def getCordinatorbyId(request, id):
    cordinatorlist = Coordinator.objects.get(id=id)
    serializer = CoordinatorSerializer(cordinatorlist, many=False)
    return Response(serializer.data)


@api_view(["GET", "POST"])
def getEventTypes(request):
    if request.method == "GET":
        type_list = EventType.objects.all()
        return pagination(request, type_list, "eventyplelisting")

    if request.method == "POST":
        serializer = EventTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def getEventCategory(request):
    if request.method == "GET":
        type_list = EventType.objects.all()[:3]
        serializer = EventTypeSerializerListing(type_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Coordinator view


class CoordinatorLogin(APIView):
    def post(self, request):
        data = request.data

        username = data["username"]
        password = data["password"]
        coordinator = Coordinator.objects.filter(username=username).first()
        if coordinator is not None and coordinator.check_password(password):
            print(coordinator)

            serializer = CoordinatorSerializer(coordinator, many=False)
            payload = {
                "username": username,
                "email": coordinator.email,
                "password": password,
            }
            jwt_token = jwt.encode(payload, "secret", algorithm="HS256")
            return Response({"data": serializer.data, "cord_jwt": jwt_token})
            # else:
            #     return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(
                {"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


@api_view(["POST"])
def cordinator_signup(request):
    data = request.data
    print("backendsignup", data)
    try:
        print(data["email"])
        cord = Coordinator.objects.create(
            username=data["email"],
            email=data["email"],
            phone_number=int(data["phone_number"]),
            password=make_password(data["password"]),
        )
        serializer = CoordinatorSerializer(cord, many=False)
        print("serializer.data", serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        message = {"detail": "username taken"}
        print(e)
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


# users view


@api_view(["POST"])
def signup(request):
    data = request.data
    print(data, "backendsignupp ")
    try:
        user = MyUser.objects.create(
            username=data["email"],
            email=data["email"],
            password=make_password(data["password"]),
            first_name=data["firstname"],
            last_name=data["lastname"],
        )
        serializer = MyUserSerializer(user, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        message = {"detail": "username taken"}
        print(e)
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    try:
        user = authenticate(username=username, password=password)
        serial = MyUserSerializer(user, many=False)
        if user:
            payload = {
                "username": username,
                "email": user.email,
                "password": user.password,
            }
            jwt_token = jwt.encode(payload, "secret", algorithm="HS256")
            return Response({"data": serial.data, "user_jwt": jwt_token})
        else:
            message = {"message": "Invalid credentials"}
            return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        message = {"message": "Invalid credentials"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["GET"])
def event_coordinator_list(request):
    event_coordinators = EventCoordinator.objects.all()
    return pagination(request, event_coordinators, "eventcoord")


@api_view(["GET"])
def event_coordinator_detail(request, id):
    try:
        event_coordinators = EventCoordinator.objects.filter(
            coordinator__id=id
        ).order_by("-id")
        return pagination(request, event_coordinators, "eventcoord")
    except EventCoordinator.DoesNotExist:
        message = {"message": "Event Coordinator not found"}
        return Response(message, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        message = {"message": "Error in Listing Event Coordinator Details"}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT"])
def event_coordinator_detail_with_id(request, id):
    try:
        event_coordinators = EventCoordinator.objects.get(id=id)
    except Item.DoesNotExist:
        return Response(
            {"message": "Event Coordinator not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        serializer = EventCoordinatorSerializer(event_coordinators)
        serialized_data = serializer.data
        return Response(serialized_data)

    elif request.method == "PUT":
        datas = request.data
        credential = get_object_or_404(EventCoordinator, id__iexact=id)
        serializer = EventCoordinatorSerializer(
            credential, data=datas["updatedData"], partial=True
        )

        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def create_event_coordinator(request):
    event_id = request.data.get("event")
    coordinator_id = request.data.get("coordinator")

    event = Event.objects.get(id=event_id)

    coordinator = Coordinator.objects.get(id=coordinator_id)

    serializer = EventCoordinatorSerializer(data=request.data)
    if serializer.is_valid():
        serializer.validated_data["event"] = event
        serializer.validated_data["coordinator"] = coordinator
        serializer.save()

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def getCoordinatorEvents(request):
    if request.method == "GET":
        type_list = EventCoordinator.objects.all()
        return pagination(request, type_list, "eventcoord")


class Coordinators(APIView):
    def get_object(self, id):
        try:
            return Coordinator.objects.get(id=id)
        except Coordinator.DoesNotExist:
            raise NotFound("Object not found")

    def get(self, request, id):
        obj = self.get_object(id)
        serializer = CoordinatorSerializer(obj)
        return Response(serializer.data)

    def put(self, request, id):
        obj = self.get_object(id)
        serializer = CoordinatorSerializer(
            obj, data=request.data, partial=True
        )  # Use partial=True

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        obj = self.get_object(id)
        obj.delete()
        return Response(status=status.HTTP_400_BAD_REQUEST)


class VenderLogin(APIView):
    def post(self, request):
        data = request.data

        email = data["email"]
        password = data["password"]
        vender = Venders.objects.filter(email=email).first()
        if vender is not None and vender.check_password(password):
            print(vender)

            serializer = VenderSerializer(vender, many=False)
            payload = {
                "username": vender.username,
                "email": email,
                "password": password,
            }
            jwt_token = jwt.encode(payload, "secret", algorithm="HS256")
            return Response({"data": serializer.data, "vender_jwt": jwt_token})

        else:
            return Response(
                {"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


@api_view(["POST"])
def vender_signup(request):
    data = request.data

    try:
        print(data["email"])
        vender = Venders.objects.create(
            username=data["email"],
            email=data["email"],
            phone_number=int(data["phone_number"]),
            password=make_password(data["password"]),
        )
        serializer = VenderSerializer(vender, many=False)
        print("serializer.data", serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        message = {"detail": "username taken"}
        print(e)
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT"])
def getVenderbyId(request, id):
    vender = Venders.objects.get(id=id)
    if request.method == "GET":
        serializer = VenderSerializer(vender, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    if request.method == "PUT":
        print(request.data)
        serializer = VenderSerializer(vender, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )


@api_view(["GET", "PUT"])
def getEventTypesbyId(request, id):
    category = EventType.objects.get(id=id)
    if request.method == "GET":
        serializer = EventTypeSerializer(category, many=False)
        return Response(serializer.data)

    if request.method == "PUT":
        serializer = EventTypeSerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )


@api_view(["GET"])
def getVenders(request):
    vender = Venders.objects.all()
    return pagination(request, vender, "vender")


@api_view(["GET"])
def get_all_items_by_supplierID(request, id):
    print(id)
    items = Item.objects.filter(supplier__id=id).order_by("-id")
    return pagination(request, items, "items")


@api_view(["GET", "POST"])
def getCategory(request):
    if request.method == "GET":
        items = Category.objects.all()
        return pagination(request, items, "category")
    if request.method == "POST":
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_platoons(request):
    platoons = Platoon.objects.all()
    serializer = PlatoonSerializer(platoons, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_cars(request):
    cars = Car.objects.all()
    serializer = CarSerializer(cars, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_flower_decorations(request):
    flower_decorations = FlowerDecoration.objects.all()
    serializer = FlowerDecorationSerializer(flower_decorations, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_floor_mats(request):
    floor_mats = FloorMat.objects.all()
    serializer = FloorMatSerializer(floor_mats, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def getEventOrders(request, id):
    order = EventUserBook.objects.filter(user__id=id)
    paginator = Paginator(order, 3)  # Number of items per page
    page = request.GET.get("page", 1)
    try:
        lists = paginator.page(page)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    serializer = EventUserBookSerializer(lists, many=True)
    pagination_data = {
        "hasNextPage": lists.has_next(),
        "hasPrevPage": lists.has_previous(),
        "currentPage": lists.number,
        "totalPages": paginator.num_pages,
        "results": serializer.data,
    }
    return Response(pagination_data)


@api_view(["PATCH"])
def BlockUsers(request, id):
    try:
        user = MyUser.objects.get(id=id)
    except MyUser.DoesNotExist:
        return Response("User not found", status=status.HTTP_404_NOT_FOUND)

    user.is_active = False  # Assuming setting is_active to False blocks the user
    user.save()

    users = MyUser.objects.all().exclude(is_superuser=True)

    return pagination(request, users, "user")


@api_view(["PATCH"])
def UnBlockUsers(request, id):
    try:
        user = MyUser.objects.get(id=id)
    except MyUser.DoesNotExist:
        return Response("User not found", status=status.HTTP_404_NOT_FOUND)

    user.is_active = True  # Assuming setting is_active to False blocks the user
    user.save()
    users = MyUser.objects.all().exclude(is_superuser=True)
    return pagination(request, users, "user")


@api_view(["GET"])
def SearchUser(request, key):
    try:
        user = MyUser.objects.filter(username__icontains=key).exclude(is_superuser=True)
    except MyUser.DoesNotExist:
        return Response("User not found", status=status.HTTP_404_NOT_FOUND)
    return pagination(request, user, "user")


@api_view(["GET"])
def SearchCoordinatorUser(request, key):
    try:
        user = Coordinator.objects.filter(username__icontains=key)
    except MyUser.DoesNotExist:
        return Response("User not found", status=status.HTTP_404_NOT_FOUND)
    return pagination(request, user, "cord")


@api_view(["PATCH"])
def BlockCordUsers(request, id):
    print(id)
    try:
        user = Coordinator.objects.get(id=id)
    except Coordinator.DoesNotExist:
        return Response("User not found", status=status.HTTP_404_NOT_FOUND)

    user.is_active = False
    user.save()

    users = Coordinator.objects.all()

    return pagination(request, users, "cord")


@api_view(["PATCH"])
def UnBlockCordUsers(request, id):
    try:
        user = Coordinator.objects.get(id=id)
    except Coordinator.DoesNotExist:
        return Response("User not found", status=status.HTTP_404_NOT_FOUND)
    print(user)

    user.is_active = True
    user.save()

    users = Coordinator.objects.all()
    return pagination(request, users, "cord")


@api_view(["GET"])
def SearchVenderUser(request, key):
    try:
        user = Venders.objects.filter(username__icontains=key)
    except Venders.DoesNotExist:
        return Response("Vender users  not found", status=status.HTTP_404_NOT_FOUND)
    return pagination(request, user, "vender")


@api_view(["PATCH"])
def BlockVendersUsers(request, id):
    try:
        user = Venders.objects.get(id=id)
    except Venders.DoesNotExist:
        return Response("User not found", status=status.HTTP_404_NOT_FOUND)
    print(user)

    user.is_active = False
    user.save()

    users = Venders.objects.all()

    return pagination(request, users, "vender")


@api_view(["PATCH"])
def UnBlockVendersUsers(request, id):
    try:
        user = Venders.objects.get(id=id)
    except Venders.DoesNotExist:
        return Response("User not found", status=status.HTTP_404_NOT_FOUND)
    print(user)

    user.is_active = True
    user.save()

    users = Venders.objects.all()
    return pagination(request, users, "vender")


@api_view(["GET"])
def SearchCategory(request, key):
    try:
        user = EventType.objects.filter(name__icontains=key)
    except EventType.DoesNotExist:
        return Response("Category users  not found", status=status.HTTP_404_NOT_FOUND)
    return pagination(request, user, "eventType")


@api_view(["GET"])
def SearchEvents(request, key):
    try:
        user = Event.objects.filter(name__icontains=key)
    except Event.DoesNotExist:
        return Response("Category users  not found", status=status.HTTP_404_NOT_FOUND)
    return pagination(request, user, "event")


@api_view(["GET"])
def SearchCoordintorEvents(request, key):
    try:
        user = EventCoordinator.objects.filter(
            Q(event__name__icontains=key) | Q(coordinator__username__icontains=key)
        )
    except Event.DoesNotExist:
        return Response("Event not found", status=status.HTTP_404_NOT_FOUND)
    return pagination(request, user, "eventcoord")


@api_view(["GET"])
def SearchItemsCategory(request, key):
    try:
        user = Category.objects.filter(name__icontains=key)
    except Category.DoesNotExist:
        return Response("category not found", status=status.HTTP_404_NOT_FOUND)
    return pagination(request, user, "category")


@api_view(["GET"])
def getUserEventBookings(request):
    eventusers = EventUserBook.objects.all()
    return pagination(request, eventusers, "eventorders")


@api_view(["GET"])
def getUserItemsBookings(request):
    eventusers = ItemUserRent.objects.all()
    return pagination(request, eventusers, "itemsorders")


@api_view(["GET"])
def SearchUserEventBookings(request, key):
    try:
        user = EventUserBook.objects.filter(
            Q(event__event__name__icontains=key)
            | Q(event__coordinator__username__icontains=key)
        )
    except EventUserBook.DoesNotExist:
        return Response("Event orders not found", status=status.HTTP_404_NOT_FOUND)
    return pagination(request, user, "eventorders")


@api_view(["GET"])
def SearchUserItemBookings(request, key):
    try:
        user = ItemUserRent.objects.filter(
            Q(item__name__icontains=key) | Q(user__username__icontains=key)
        )
    except ItemUserRent.DoesNotExist:
        return Response("Items orders not found", status=status.HTTP_404_NOT_FOUND)
    return pagination(request, user, "itemsorders")


@api_view(["GET"])
def SearchSuppliersItem(request, key):
    try:
        user = Item.objects.filter(
            Q(name__icontains=key) | Q(supplier__username__icontains=key)
        )
    except Item.DoesNotExist:
        return Response("Items orders not found", status=status.HTTP_404_NOT_FOUND)
    return pagination(request, user, "items")


@api_view(["GET"])
def UserEventBookingsBycordId(request, id):
    try:
        user = EventUserBook.objects.filter(event__coordinator__id=id)
    except EventUserBook.DoesNotExist:
        return Response("Event orders not found", status=status.HTTP_404_NOT_FOUND)
    return pagination(request, user, "eventorders")


@api_view(["PATCH"])
def approveUser(request, id):
    try:
        event = EventUserBook.objects.get(id=id)
    except EventUserBook.DoesNotExist:
        return Response("User not found", status=status.HTTP_404_NOT_FOUND)

    event.is_approved = True
    event.save()

    events = EventUserBook.objects.filter(
        event__coordinator__username=event.event.coordinator
    )
    return pagination(request, events, "eventorders")


@api_view(["PATCH"])
def unapproveUser(request, id):
    try:
        event = EventUserBook.objects.get(id=id)
    except EventUserBook.DoesNotExist:
        return Response("User not found", status=status.HTTP_404_NOT_FOUND)

    if event.is_paid == True:
        return Response("User already Paid", status=status.HTTP_406_NOT_ACCEPTABLE)

    event.is_approved = False
    event.save()

    events = EventUserBook.objects.filter(event__coordinator=event.event.coordinator)
    return pagination(request, events, "eventorders")


@api_view(["POST"])
def create_item(request):
    data = request.data.copy()  # Create a mutable copy of the request data
    print(data)
    try:
        supplier_id = int(data.get("supplier"))
        supplier = Venders.objects.get(id=supplier_id)
    except Venders.DoesNotExist:
        return Response(
            {"error": "Invalid supplier ID"}, status=status.HTTP_400_BAD_REQUEST
        )

    data["supplier"] = supplier.id  # Assign the ID of the supplier

    item_type = data.get("item_type")
    serializer_class = None

    if item_type == "Car":
        serializer_class = CarSerializer
    elif item_type == "Platoon":
        serializer_class = PlatoonSerializer
    elif item_type == "FlowerDecoration":
        serializer_class = FlowerDecorationSerializer
    elif item_type == "FloorMat":
        serializer_class = FloorMatSerializer
    else:
        return Response(
            {"error": f"Invalid item type: {item_type}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = serializer_class(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_items(request):
    items = Item.objects.all().order_by("-id")
    page = request.GET.get("page", 1)
    paginator = Paginator(items, 5)  # Number of items per page

    try:
        lists = paginator.page(page)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    serializer = ItemSerializer(lists, many=True)
    data = serializer.data

    # Fetch subclass details for each item
    for item_data in data:
        item_id = item_data["id"]
        item_type = item_data["item_type"]

        if item_type == "Car":
            try:
                car = Car.objects.get(id=item_id)
                car_serializer = CarSerializer(car)
                item_data["car_details"] = car_serializer.data
            except Car.DoesNotExist:
                pass
        elif item_type == "FloorMat":
            try:
                floor_mat = FloorMat.objects.get(id=item_id)
                floor_mat_serializer = FloorMatSerializer(floor_mat)
                item_data["floor_mat_details"] = floor_mat_serializer.data
            except FloorMat.DoesNotExist:
                pass
        elif item_type == "FlowerDecoration":
            try:
                flower_decoration = FlowerDecoration.objects.get(id=item_id)
                flower_decoration_serializer = FlowerDecorationSerializer(
                    flower_decoration
                )
                item_data[
                    "flower_decoration_details"
                ] = flower_decoration_serializer.data
            except FlowerDecoration.DoesNotExist:
                pass
        elif item_type == "Platoon":
            try:
                platoon = Platoon.objects.get(id=item_id)
                platoon_serializer = PlatoonSerializer(platoon)
                item_data["platoon_details"] = platoon_serializer.data
            except Platoon.DoesNotExist:
                pass

        # Add similar conditions for other item types

    pagination_data = {
        "hasNextPage": lists.has_next(),
        "hasPrevPage": lists.has_previous(),
        "currentPage": lists.number,
        "totalPages": paginator.num_pages,
        "results": serializer.data,
    }

    return Response(pagination_data)


@api_view(["GET", "PUT"])
def item_detail_by_type(request, item_type, id):
    try:
        item = Item.objects.select_related(
            "car", "floormat", "flowerdecoration", "platoon"
        ).get(id=id)
    except Item.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if item.item_type != item_type:
        return Response(
            {"message": "Invalid item type"}, status=status.HTTP_400_BAD_REQUEST
        )

    if request.method == "GET":
        serializer = None
        if item_type == "Car":
            serializer = CarSerializer(item.car)
        elif item_type == "FloorMat":
            serializer = FloorMatSerializer(item.floormat)
        elif item_type == "FlowerDecoration":
            serializer = FlowerDecorationSerializer(item.flowerdecoration)
        elif item_type == "Platoon":
            serializer = PlatoonSerializer(item.platoon)
        else:
            return Response(
                {"message": "Invalid item type"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "PUT":
        if item_type == "Car":
            serializer = CarSerializer(
                item.car, data=request.data["datas"], partial=True
            )
        elif item_type == "FloorMat":
            floormat = item.floormat
            serializer = FloorMatSerializer(
                floormat, data=request.data["datas"], partial=True
            )
        elif item_type == "FlowerDecoration":
            flower_decoration = item.flowerdecoration
            serializer = FlowerDecorationSerializer(
                flower_decoration, data=request.data["datas"], partial=True
            )
        elif item_type == "Platoon":
            platoon = item.platoon
            serializer = PlatoonSerializer(
                platoon, data=request.data["datas"], partial=True
            )
        else:
            return Response(
                {"message": "Invalid item type"}, status=status.HTTP_400_BAD_REQUEST
            )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {"message": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
    )


@api_view(["GET", "POST"])
def user_item_Booking(request):
    if request.method == "GET":
        item_rental = ItemUserRent.objects.filter(is_paid=True)
        page = request.GET.get("page", 1)
        paginator = Paginator(item_rental, 4)  # Number of items per page

        try:
            lists = paginator.page(page)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ItemUserRentSerializer(lists, many=True)
        pagination_data = {
            "hasNextPage": lists.has_next(),
            "hasPrevPage": lists.has_previous(),
            "currentPage": lists.number,
            "totalPages": paginator.num_pages,
            "results": serializer.data,
        }

        return Response(pagination_data)

    if request.method == "POST":
        item_name = request.data.get("item")
        user_username = request.data.get("user")
        selected_date_str = request.data.get("selectedDates")
        quantity = request.data.get("quantity")

        print(user_username)

        item = Item.objects.filter(name__iexact=item_name).first()
        user = MyUser.objects.filter(username=user_username).first()

        if not item or not user or not  quantity or not selected_date_str:
            return Response("Input cannot be empty", status=status.HTTP_400_BAD_REQUEST)

        try:
            selected_date = make_aware(
                datetime.strptime(selected_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            ).date()
            date_bookto = selected_date + timedelta(days=3)
        except ValueError:
            print("dateformat error")
            return Response("Invalid date format", status=status.HTTP_400_BAD_REQUEST)

        # Check if the event booking already exists
        existing_booking = ItemUserRent.objects.filter(
            user=user,
            item=item,
            date_booked=selected_date,
            date_bookedto=date_bookto,
            quantity=quantity,
        ).first()
        existing_bookingondate = ItemUserRent.objects.filter(
            date_booked=selected_date,
            date_bookedto=date_bookto,
        ).first()
        if existing_booking or existing_bookingondate:
            return Response("Item already booked", status=status.HTTP_400_BAD_REQUEST)

        item_user_rent = ItemUserRent.objects.create(
            user=user,
            item=item,
            date_booked=selected_date,
            date_bookedto=date_bookto,
            quantity=quantity,  # Adjust the quantity as needed
        )
        serializer = ItemUserRentCreateSerializer(item_user_rent)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def user_Booking_list_by_Suppler_id(request, id):
    if request.method == "GET":
        item_Bookings = ItemUserRent.objects.filter(item__supplier__id=id).order_by(
            "-id"
        )
        page = request.GET.get("page", 1)
        paginator = Paginator(item_Bookings, 4)  # Number of items per page

        try:
            lists = paginator.page(page)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ItemUserRentSerializer(lists, many=True)
        pagination_data = {
            "hasNextPage": lists.has_next(),
            "hasPrevPage": lists.has_previous(),
            "currentPage": lists.number,
            "totalPages": paginator.num_pages,
            "results": serializer.data,
        }

        return Response(pagination_data)


@api_view(["GET"])
def user_Paid_list_by_Suppler_id(request, id):
    if request.method == "GET":
        item_Bookings = ItemUserRent.objects.filter(
            item__supplier__id=id, is_paid=True
        ).order_by("-id")
        page = request.GET.get("page", 1)
        paginator = Paginator(item_Bookings, 4)  # Number of items per page

        try:
            lists = paginator.page(page)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ItemUserRentSerializer(lists, many=True)
        pagination_data = {
            "hasNextPage": lists.has_next(),
            "hasPrevPage": lists.has_previous(),
            "currentPage": lists.number,
            "totalPages": paginator.num_pages,
            "results": serializer.data,
        }

        return Response(pagination_data)


@api_view(["GET"])
def approvedBookingListbyUserId(request, id):
    try:
        item_bookings = ItemUserRent.objects.filter(
            user_id=id, is_approved=True
        ).order_by("-id")

        paginator = Paginator(item_bookings, 4)  # Number of items per page
        page = request.GET.get("page", 1)
        lists = paginator.get_page(page)

        serializer = ItemUserRentSerializer(lists, many=True)

        pagination_data = {
            "hasNextPage": lists.has_next(),
            "hasPrevPage": lists.has_previous(),
            "currentPage": lists.number,
            "totalPages": paginator.num_pages,
            "results": serializer.data,
        }

        return Response(pagination_data)

    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def paidBookingListbyUserId(request, id):
    if request.method == "GET":
        item_bookings = ItemUserRent.objects.filter(
            user_id=id, is_approved=True, is_paid=True
        ).order_by("-id")
        page = request.GET.get("page", 1)
        paginator = Paginator(item_bookings, 4)  # Number of items per page

        try:
            lists = paginator.page(page)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ItemUserRentSerializer(lists, many=True)
        pagination_data = {
            "hasNextPage": lists.has_next(),
            "hasPrevPage": lists.has_previous(),
            "currentPage": lists.number,
            "totalPages": paginator.num_pages,
            "results": serializer.data,
        }

        return Response(pagination_data)


@api_view(["GET"])
def unapprovedBookingListbyUserId(request, id):
    if request.method == "GET":
        item_bookings = ItemUserRent.objects.filter(
            user_id=id, is_approved=False
        ).order_by("-id")

        page = request.GET.get("page", 1)
        paginator = Paginator(item_bookings, 4)  # Number of items per page

        try:
            lists = paginator.page(page)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ItemUserRentSerializer(lists, many=True)
        pagination_data = {
            "hasNextPage": lists.has_next(),
            "hasPrevPage": lists.has_previous(),
            "currentPage": lists.number,
            "totalPages": paginator.num_pages,
            "results": serializer.data,
        }

        return Response(pagination_data)


@api_view(["PATCH"])
def approveUserItems(request, id):
    try:
        event = ItemUserRent.objects.get(id=id)
    except ItemUserRent.DoesNotExist:
        return Response("User not found", status=status.HTTP_404_NOT_FOUND)

    event.is_approved = True
    event.save()
    return Response(status.HTTP_200_OK)


@api_view(["POST"])
def create_checkout_session(request):
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    amount = 1
    name = request.data.get("name")

    # TODO: Customize the session creation based on your requirements
    session = client.order.create(
        {
            # Convert amount to paise (Rupee to Paisa conversion)
            "amount": amount * 100,
            "currency": "INR",
            "payment_capture": "1",
        }
    )

    order_id = session["id"]
    # Replace with your actual checkout URL
    checkout_url = f"https://localhost:8000/checkout/{order_id}"

    response_data = {
        "key": settings.RAZORPAY_KEY_ID,
        "amount": session["amount"],
        "currency": session["currency"],
        "name": name,
        "order_id": order_id,
        "checkout_url": checkout_url,
    }
    return Response({"payment": response_data})


@api_view(["POST"])
def verify_payment(request):
    payment_id = request.data.get("payment_id")
    row_id = request.data.get("row_id")

    try:
        # Retrieve the booking based on the row_id
        booking = ItemUserRent.objects.get(id=row_id)
        booking.is_paid = True
        booking.payment_id = payment_id
        booking.save()

        return Response({"message": "Payment verified successfully."})
    except ItemUserRent.DoesNotExist:
        return Response(
            {"error": "Booking does not exist."}, status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
def verify_event_payment(request):
    payment_id = request.data.get("payment_id")
    row_id = request.data.get("row_id")

    try:
        # Retrieve the booking based on the row_id
        booking = EventUserBook.objects.get(id=row_id, is_approved=True)
        booking.is_paid = True
        booking.payment_id = payment_id
        booking.save()

        return Response({"message": "Payment verified successfully."})
    except EventUserBook.DoesNotExist:
        return Response(
            {"error": "Booking does not exist."}, status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response({"error": str(e)}, status=500)


# item User Booking Sections


@api_view(["POST", "GET"])
def events_user_Booking(request):
    if request.method == "GET":
        event_booking = EventUserBook.objects.filter(is_paid=True)
        page = request.GET.get("page", 1)
        paginator = Paginator(event_booking, 4)  # Number of items per page

        try:
            lists = paginator.page(page)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = EventUserBookSerializer(lists, many=True)
        pagination_data = {
            "hasNextPage": lists.has_next(),
            "hasPrevPage": lists.has_previous(),
            "currentPage": lists.number,
            "totalPages": paginator.num_pages,
            "results": serializer.data,
        }

        return Response(pagination_data)

    if request.method == "POST":
        event_id = request.data.get("event")
        userid = request.data.get("user")
        selected_date_str = request.data.get("selectedDatefrom")
        selected_dateto_str = request.data.get("selectedDateto")

        try:
            event = EventCoordinator.objects.get(id=event_id)
            user = MyUser.objects.filter(username=userid).first()
            if not event or not user:
                return Response(
                    "Invalid Event or user", status=status.HTTP_400_BAD_REQUEST
                )

            try:
                selected_date = datetime.strptime(
                    selected_date_str, "%Y-%m-%dT%H:%M:%S.%fZ"
                ).date()
                selected_dateato = datetime.strptime(
                    selected_dateto_str, "%Y-%m-%dT%H:%M:%S.%fZ"
                ).date()
            except ValueError:
                return Response(
                    "Invalid date format", status=status.HTTP_400_BAD_REQUEST
                )

            # Check if the event booking already exists
            existing_booking = EventUserBook.objects.filter(
                event=event, user=user, date_booked=selected_date
            ).first()
            if existing_booking:
                return Response(
                    "Event booking already exists", status=status.HTTP_400_BAD_REQUEST
                )

            event_booked = EventUserBook.objects.create(
                user=user,
                event=event,
                date_booked=selected_date,
                date_bookedto=selected_dateato,
                is_approved=False,
            )

            serializer = EventUserBookSerializer(event_booked)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def approvedEventBookingListbyUserId(request, id):
    if request.method == "GET":
        event_booking = EventUserBook.objects.filter(
            user_id=id, is_approved=True, is_paid=False
        ).order_by("-id")
        page = request.GET.get("page", 1)
        paginator = Paginator(event_booking, 4)  # Number of items per page

        try:
            lists = paginator.page(page)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = EventUserBookSerializer(lists, many=True)
        pagination_data = {
            "hasNextPage": lists.has_next(),
            "hasPrevPage": lists.has_previous(),
            "currentPage": lists.number,
            "totalPages": paginator.num_pages,
            "results": serializer.data,
        }

        return Response(pagination_data)


@api_view(["GET"])
def approvedEventBookingListbysupplierId(request, id):
    if request.method == "GET":
        event_booking = EventUserBook.objects.filter(
            event__coordinator__id=id, is_approved=True, is_paid=False
        ).order_by("-id")
        page = request.GET.get("page", 1)
        paginator = Paginator(event_booking, 4)  # Number of items per page

        try:
            lists = paginator.page(page)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = EventUserBookSerializer(lists, many=True)
        pagination_data = {
            "hasNextPage": lists.has_next(),
            "hasPrevPage": lists.has_previous(),
            "currentPage": lists.number,
            "totalPages": paginator.num_pages,
            "results": serializer.data,
        }

        return Response(pagination_data)


@api_view(["GET"])
def PaidEventBookingListbysupplierId(request, id):
    if request.method == "GET":
        event_booking = EventUserBook.objects.filter(
            is_approved=True, is_paid=True
        ).order_by("-id")
        page = request.GET.get("page", 1)
        paginator = Paginator(event_booking, 4)  # Number of items per page

        try:
            lists = paginator.page(page)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = EventUserBookSerializer(lists, many=True)
        pagination_data = {
            "hasNextPage": lists.has_next(),
            "hasPrevPage": lists.has_previous(),
            "currentPage": lists.number,
            "totalPages": paginator.num_pages,
            "results": serializer.data,
        }

        return Response(pagination_data)


@api_view(["GET"])
def nonapprovedEventBookingListbysupplierId(request, id):
    if request.method == "GET":
        event_booking = EventUserBook.objects.filter(
            event__coordinator__id=id, is_approved=False
        ).order_by("-id")
        page = request.GET.get("page", 1)
        paginator = Paginator(event_booking, 4)  # Number of items per page

        try:
            lists = paginator.page(page)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = EventUserBookSerializer(lists, many=True)
        pagination_data = {
            "hasNextPage": lists.has_next(),
            "hasPrevPage": lists.has_previous(),
            "currentPage": lists.number,
            "totalPages": paginator.num_pages,
            "results": serializer.data,
        }

        return Response(pagination_data)


@api_view(["GET"])
def paidEventBookingListbyUserId(request, id):
    if request.method == "GET":
        item_bookings = EventUserBook.objects.filter(
            user_id=id, is_approved=True, is_paid=True
        ).order_by("-id")
        page = request.GET.get("page", 1)
        paginator = Paginator(item_bookings, 4)  # Number of items per page

        try:
            lists = paginator.page(page)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = EventUserBookSerializer(lists, many=True)
        pagination_data = {
            "hasNextPage": lists.has_next(),
            "hasPrevPage": lists.has_previous(),
            "currentPage": lists.number,
            "totalPages": paginator.num_pages,
            "results": serializer.data,
        }

        return Response(pagination_data)


@api_view(["GET"])
def unapprovedEventBookingListbyUserId(request, id):
    if request.method == "GET":
        item_bookings = EventUserBook.objects.filter(
            user_id=id, is_approved=False
        ).order_by("-id")


        page = request.GET.get("page", 1)
        paginator = Paginator(item_bookings, 4)  # Number of items per page

        try:
            lists = paginator.page(page)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = EventUserBookSerializer(lists, many=True)
        pagination_data = {
            "hasNextPage": lists.has_next(),
            "hasPrevPage": lists.has_previous(),
            "currentPage": lists.number,
            "totalPages": paginator.num_pages,
            "results": serializer.data,
        }

        return Response(pagination_data)


@api_view(["GET"])
def get_Eventorders_by_date(request, date):
    if request.method == "GET":
        try:
            print(date)
            orders = EventUserBook.objects.filter(date_booked=date)
            print(orders)
            serializer = EventUserBookSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:
        return Response(
            {"message": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET"])
def get_monthly_revenue(request):
    try:
        bookings = EventUserBook.objects.values("date_booked__month").annotate(
            total_revenue=Sum("event__price")
        )

        monthly_revenue = {}
        for booking in bookings:
            month = booking["date_booked__month"]
            revenue = booking["total_revenue"]
            monthly_revenue[month] = revenue

        monthly_data = []
        for month in range(1, 13):
            monthly_data.append(monthly_revenue.get(month, None))

        return Response(monthly_data, status=status.HTTP_200_OK)

    except Exception as e:
        print(str(e))
        return Response(
            {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
def get_yearly_revenue(request):
    try:
        bookings = EventUserBook.objects.values("date_booked__year").annotate(
            total_revenue=Sum("event__price")
        )

        yearly_revenue = {}
        for booking in bookings:
            year = booking["date_booked__year"]
            revenue = booking["total_revenue"]
            yearly_revenue[year] = revenue

        return Response(yearly_revenue, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
def get_weekly_revenue(request):
    try:
        # Calculate weekly revenue by grouping bookings by week
        bookings = EventUserBook.objects.values("date_booked__week").annotate(
            total_revenue=Sum("event__price")
        )

        weekly_revenue = {}
        for booking in bookings:
            week = booking["date_booked__week"]
            revenue = booking["total_revenue"]
            weekly_revenue[week] = revenue

        return Response(weekly_revenue, status=200)
    except Exception as e:
        return Response({"message": str(e)}, status=500)


@api_view(["GET"])
def get_Itemorders_by_date(request, date):
    try:
        # Retrieve orders for the specified date
        orders = ItemUserRent.objects.filter(date_booked=date)

        order_data = []  # Prepare the data to be sent in the response
        for order in orders:
            order_data.append(
                {
                    "revenue": order.item.price * order.quantity,
                    "quantity": order.quantity,
                }
            )

        return Response(order_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
def get_Itemmonthly_revenue(request):
    try:
        bookings = ItemUserRent.objects.values("date_booked__month").annotate(
            total_revenue=Sum("item__price")
        )

        print(bookings)

        monthly_revenue = {}
        for booking in bookings:
            month = booking["date_booked__month"]
            revenue = booking["total_revenue"]
            monthly_revenue[month] = revenue

        monthly_data = []
        for month in range(1, 13):
            monthly_data.append(monthly_revenue.get(month, None))

        return Response(monthly_data, status=status.HTTP_200_OK)

    except Exception as e:
        print(str(e))
        return Response(
            {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
def get_Itemyearly_revenue(request):
    try:
        bookings = ItemUserRent.objects.values("date_booked__year").annotate(
            total_revenue=Sum("item__price")
        )

        yearly_revenue = {}
        for booking in bookings:
            year = booking["date_booked__year"]
            revenue = booking["total_revenue"]
            yearly_revenue[year] = revenue

        return Response(yearly_revenue, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
def get_Itemweekly_revenue(request):
    try:
        # Calculate weekly revenue by grouping bookings by week
        bookings = ItemUserRent.objects.values("date_booked__week").annotate(
            total_revenue=Sum("item__price")
        )

        weekly_revenue = {}
        for booking in bookings:
            week = booking["date_booked__week"]
            revenue = booking["total_revenue"]
            weekly_revenue[week] = revenue

        return Response(weekly_revenue, status=200)
    except Exception as e:
        return Response({"message": str(e)}, status=500)


@api_view(["GET"])
def coordinator_booking_count(request, id):
    try:
        coordinator = Coordinator.objects.get(id=id)
        booking_count = EventUserBook.objects.filter(
            event__coordinator=coordinator
        ).count()
        return Response({"booking_count": booking_count})
    except Coordinator.DoesNotExist:
        return Response({"error": "Coordinator not found"}, status=404)


class EventUserBookDetailView(RetrieveUpdateAPIView):
    queryset = EventUserBook.objects.all()
    serializer_class = EventUserBookSerializer
    lookup_field = "pk"


@api_view(["GET"])
def coordinator_events_count(request, id):
    try:
        coordinator = Coordinator.objects.get(id=id)
        booking_count = EventCoordinator.objects.filter(coordinator=coordinator).count()
        return Response({"booking_count": booking_count})
    except Coordinator.DoesNotExist:
        return Response({"error": "Coordinator not found"}, status=404)


@api_view(["GET"])
def coordinator_earning(request, id):
    try:
        coordinator = Coordinator.objects.get(id=id)
        bookings = EventUserBook.objects.filter(event__coordinator=coordinator)
        total_earnings = sum(booking.event.price for booking in bookings)
        return Response({"total_earnings": total_earnings})
    except Coordinator.DoesNotExist:
        return Response({"error": "Coordinator not found"}, status=404)


@api_view(["GET"])
def supplier_booking_count(request, id):
    try:
        vender = Venders.objects.get(id=id)
        booking_count = ItemUserRent.objects.filter(item__supplier=vender).count()
        return Response({"booking_count": booking_count})
    except Coordinator.DoesNotExist:
        return Response({"error": "Coordinator not found"}, status=404)


@api_view(["GET"])
def supplier_Items_count(request, id):
    try:
        vender = Venders.objects.get(id=id)
        booking_count = Item.objects.filter(supplier=vender).count()
        return Response({"booking_count": booking_count})
    except Coordinator.DoesNotExist:
        return Response({"error": "Coordinator not found"}, status=404)


@api_view(["GET"])
def supplier_earning(request, id):
    try:
        vender = Venders.objects.get(id=id)
        bookings = ItemUserRent.objects.filter(item__supplier=vender)
        total_earnings = sum(booking.item.price for booking in bookings)
        return Response({"total_earnings": total_earnings})
    except Coordinator.DoesNotExist:
        return Response({"error": "Coordinator not found"}, status=404)


@api_view(["GET"])
def get_monthly_revenue_by_admin(request):
    try:
        item_revenue = ItemUserRent.objects.values("date_booked__month").annotate(
            total_revenue=Sum("item__price")
        )

        event_revenue = EventUserBook.objects.values("date_booked__month").annotate(
            total_revenue=Sum("event__price")
        )

        monthly_revenue = {}

        for item in item_revenue:
            month = item["date_booked__month"]
            revenue = item["total_revenue"]
            monthly_revenue.setdefault(month, {"total_revenue": revenue})

        for event in event_revenue:
            month = event["date_booked__month"]
            revenue = event["total_revenue"]
            if month in monthly_revenue:
                monthly_revenue[month]["total_revenue"] += revenue
            else:
                monthly_revenue.setdefault(month, {"total_revenue": revenue})

        monthly_data = []
        for month in range(1, 13):
            data = monthly_revenue.get(month, None)
            if data is not None:
                data["total_revenue"] = int(data["total_revenue"])
            monthly_data.append(data)

        return Response(monthly_data, status=status.HTTP_200_OK)

    except Exception as e:
        print(str(e))
        return Response(
            {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
def get_daily_revenue_admin(request, date):
    if request.method == "GET":
        try:
            event_revenue = EventUserBook.objects.filter(date_booked=date).aggregate(
                total_revenue=Sum("event__price")
            )
            item_revenue = ItemUserRent.objects.filter(date_booked=date).aggregate(
                total_revenue=Sum(F("item__price") * F("quantity"))
            )

            combined_revenue = (event_revenue["total_revenue"] or 0) + (
                item_revenue["total_revenue"] or 0
            )

            return Response(
                {"total_revenue": combined_revenue}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:
        return Response(
            {"message": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST
        )
