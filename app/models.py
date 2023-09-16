from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import check_password
from django.utils import timezone


class MyUser(AbstractUser):
    phone_number = models.CharField(max_length=250, unique=False)
    image = models.ImageField(upload_to="images", default="")

    def __str__(self) -> str:
        return self.username


class Coordinator(models.Model):
    username = models.CharField(max_length=255, unique=False)
    email = models.CharField(max_length=255, default='')
    approved = models.BooleanField(default=False)

    phone_number = models.CharField(max_length=255)
    imageUrl = models.CharField(max_length=300, default="")
    password = models.CharField(max_length=250, default="")
    is_active = models.BooleanField(default=True)

    def check_password(self, raw_password):
        """
        Check the password against the Coordinator's own password hash.
        """
        return check_password(raw_password, self.password)

    def __str__(self) -> str:
        return self.username


class EventType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="images", default="")
    imageUrl = models.CharField(max_length=300, default="")

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=100)
    type = models.ForeignKey(EventType, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_type_name(self):
        return self.type.name


class Package(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.name


class EventCoordinator(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    coordinator = models.ForeignKey(Coordinator, on_delete=models.CASCADE)
    capacity = models.IntegerField()
    # date_available = models.DateTimeField()
    price = models.DecimalField(max_digits=18, decimal_places=2)
    is_active = models.BooleanField(default=True)
    location = models.CharField(max_length=200, default='calicut')
    imageUrl = models.CharField(max_length=300, default="")
    description = models.TextField(default="")

    def __str__(self):
        return f"{self.coordinator.username}::{self.event.name}"


class EventUserBook(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    event = models.ForeignKey(
        EventCoordinator, on_delete=models.CASCADE, null=True)
    date_booked = models.DateField(default=timezone.now)
    date_bookedto = models.DateField(default=timezone.now)
    is_approved = models.BooleanField(default=True)
    payment_id = models.CharField(max_length=300, default="")
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return '{}: {}'.format(self.event.event.name, self.user)


class Venders(models.Model):
    username = models.CharField(max_length=255, unique=False)
    email = models.CharField(max_length=255, default='')
    approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_vender = models.BooleanField(default=True)
    phone_number = models.CharField(max_length=255)
    password = models.CharField(max_length=250, default="")
    imageUrl = models.CharField(max_length=300, default="")
    description = models.TextField(default="")

    def check_password(self, raw_password):
        """
        Check the password against the Coordinator's own password hash.
        """
        return check_password(raw_password, self.password)

    def __str__(self) -> str:
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Item(models.Model):
    ITEM_TYPES = (
        ('Car', 'Car'),
        ('FlowerDecoration', 'Flower Decoration'),
        ('FloorMat', 'Floor Mat'),
        ('Platoon', 'Platoon'),
        ('AudioEquipment', 'AudioEquipment'),
        ('LightingEquipment', 'LightingEquipment'),
        ('StageBackdrop', 'StageBackdrop'),
        ('Furniture', 'Furniture'),
        ('AudioVisualEquipment', 'AudioVisualEquipment'),
        ('CateringEquipment', 'CateringEquipment'),
    )
    name = models.CharField(max_length=100, default="")
    imageUrl = models.CharField(max_length=300, default="")
    description = models.TextField(default="")
    supplier = models.ForeignKey(
        Venders, on_delete=models.SET_NULL, null=True, blank=True)
    item_type = models.CharField(
        max_length=100, choices=ITEM_TYPES, default="")
    available = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Car(Item):
    car_model = models.CharField(max_length=100, default="")
    car_type = models.CharField(max_length=100, default="")
    seating_capacity = models.IntegerField(default=4)
    fuel_type = models.CharField(max_length=100, default="")
    transmission_type = models.CharField(max_length=100, default="")


class FlowerDecoration(Item):
    flower_type = models.CharField(max_length=100, default="")
    color_scheme = models.CharField(max_length=100, default="")
    arrangement_style = models.CharField(max_length=100, default="")
    size = models.CharField(max_length=100, default="")
    additional_decor = models.TextField(default="")


class FloorMat(Item):
    mat_material = models.CharField(max_length=100, default="")
    mat_type = models.CharField(max_length=100, default="")
    color = models.CharField(max_length=100, default="")
    size = models.CharField(max_length=100, default="")
    pattern = models.CharField(max_length=100, default="")


class Platoon(Item):
    platoon_size = models.CharField(max_length=100, default="")
    platoon_type = models.CharField(max_length=100, default="")
    platoon_uniform = models.CharField(max_length=100, default="")
    performance_style = models.CharField(max_length=100, default="")


class AudioEquipment(Item):
    equipment_type = models.CharField(max_length=100, default="")
    brand = models.CharField(max_length=100, default="")
    power_rating = models.CharField(max_length=100, default="")
    additional_info = models.TextField(default="")


class LightingEquipment(Item):
    equipment_type = models.CharField(max_length=100, default="")
    brand = models.CharField(max_length=100, default="")
    power_rating = models.CharField(max_length=100, default="")
    additional_info = models.TextField(default="")


class StageBackdrop(Item):
    backdrop_type = models.CharField(max_length=100, default="")
    size = models.CharField(max_length=100, default="")
    color = models.CharField(max_length=100, default="")
    additional_info = models.TextField()


class Furniture(Item):
    furniture_type = models.CharField(max_length=100, default="")
    material = models.CharField(max_length=100, default="")
    color = models.CharField(max_length=100, default="")
    additional_info = models.TextField(default="")


class AudioVisualEquipment(Item):
    equipment_type = models.CharField(max_length=100, default="")
    brand = models.CharField(max_length=100, default="")
    power_rating = models.CharField(max_length=100, default="")
    additional_info = models.TextField(default="")


class CateringEquipment(Item):
    equipment_type = models.CharField(max_length=100, default="")
    brand = models.CharField(max_length=100, default="")
    power_rating = models.CharField(max_length=100, default="")
    additional_info = models.TextField(default="")


class ItemUserRent(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    date_booked = models.DateField(default=timezone.now)
    date_bookedto = models.DateField(default=timezone.now)
    is_approved = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=300, default="111111111")
    quantity = models.IntegerField()

    def __str__(self):
        return '{}: {}'.format(self.item.name, self.quantity)


class Order(models.Model):
    order_item = models.ForeignKey(Item, on_delete=models.CASCADE)
    order_amount = models.CharField(max_length=25)
    order_payment_id = models.CharField(max_length=100)
    isPaid = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order_item
