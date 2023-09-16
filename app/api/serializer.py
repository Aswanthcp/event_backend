from rest_framework import serializers
from ..models import *
from datetime import datetime


class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = [
            "id",
            "username",
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "is_active",
        ]


class CoordinatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinator
        fields = [
            "id",
            "username",
            "email",
            "approved",
            "phone_number",
            "password",
            "imageUrl",
            "is_active",
        ]


class VenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venders
        fields = [
            "id",
            "username",
            "email",
            "approved",
            "is_active",
            "phone_number",
            "is_vender",
            "password",
            "imageUrl",
            "description",
        ]


class EventTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventType
        fields = ["id", "name", "description"]
        
class EventTypeSerializerListing(serializers.ModelSerializer):
    class Meta:
        model = EventType
        fields = ["id", "name", "description","imageUrl"]


class EventSerializer(serializers.ModelSerializer):
    type = EventTypeSerializer(read_only=True)

    class Meta:
        model = Event
        fields = ["id", "name", "type"]


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ["id", "name", "price", "description"]


class EventCoordinatorSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    coordinator = CoordinatorSerializer(read_only=True)

    class Meta:
        model = EventCoordinator
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "name"]


class ItemSerializer(serializers.ModelSerializer):
    supplier = VenderSerializer(read_only=True)
    item_type = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = "__all__"

    def get_item_type(self, obj):
        item_type = obj.item_type
        serializer_class = None

        if item_type == "Car":
            serializer_class = CarSerializer
        elif item_type == "FlowerDecoration":
            serializer_class = FlowerDecorationSerializer
        elif item_type == "FloorMat":
            serializer_class = FloorMatSerializer
        elif item_type == "Platoon":
            serializer_class = PlatoonSerializer

        if serializer_class is not None:
            serializer = serializer_class(obj)
            return serializer.data

        return None


class PlatoonSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)

    class Meta:
        model = Platoon
        fields = "__all__"


class CarSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)

    class Meta:
        model = Car
        fields = "__all__"


class FlowerDecorationSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)

    class Meta:
        model = FlowerDecoration
        fields = "__all__"


class FloorMatSerializer(serializers.ModelSerializer):
    # item = ItemSerializer(read_only=True)

    class Meta:
        model = FloorMat
        fields = "__all__"


class ItemUserRentCreateSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    user = MyUserSerializer(read_only=True)
    date_booked = serializers.ReadOnlyField(source="get_date_booked")
    date_bookedto = serializers.ReadOnlyField(source="get_date_bookedto")

    def get_date_booked(self, obj):
        return obj.date_booked.date()

    def get_date_bookedto(self, obj):
        return obj.date_bookedto.date()

    class Meta:
        model = ItemUserRent
        fields = "__all__"


class ItemUserRentSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    user = MyUserSerializer(read_only=True)
    date_booked = serializers.DateField()
    date_bookedto = serializers.DateField()

    def validate_date_booked(self, value):
        # Convert datetime to date if needed
        if isinstance(value, datetime):
            return value.date()
        return value

    class Meta:
        model = ItemUserRent
        fields = "__all__"


class EventUserBookSerializer(serializers.ModelSerializer):
    event = EventCoordinatorSerializer(read_only=True)
    user = MyUserSerializer(read_only=True)
    date_booked = serializers.DateField()
    date_bookedto = serializers.DateField()

    def validate_date_booked(self, value):
        # Convert datetime to date if needed
        if isinstance(value, datetime):
            return value.date()
        return value

    class Meta:
        model = EventUserBook
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    order_date = serializers.DateTimeField(format="%d %B %Y %I:%M %p")
    order_item = ItemSerializer(read_only=True)

    class Meta:
        model = Order
        fields = "__all__"
        depth = 2
