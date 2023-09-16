from datetime import datetime
from django.urls import reverse
import json
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import *
from .serializer import *


class MyUserAPITestCase(APITestCase):
    def setUp(self):
        self.user = MyUser.objects.create(
            username="testuser", phone_number="1234567890"
        )

    def tearDown(self):
        self.user.delete()

    def test_get_user(self):
        # Test the GET method to retrieve a user
        response = self.client.get("/api/getUsers/{}/".format(self.user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")

    def test_create_user(self):
        # Test the POST method to create a user
        data = {
            "username": "newuser@gmail.com",
            "phone_number": "9876543210",
            "email": "newuser@gmail.com",
            "password": "11111111",
            "firstname": "user",
            "lastname": "name",
        }
        response = self.client.post("/api/signup/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "newuser@gmail.com")

    def test_update_user(self):
        # Test the PUT method to update a user
        data = {"username": "updateduser", "phone_number": "5555555555"}
        response = self.client.put("/api/getUsers/{}/".format(self.user.id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "updateduser")
        self.assertEqual(response.data["phone_number"], "5555555555")


class CoordinatorAPITestcase(APITestCase):
    def setUp(self):
        self.user = Coordinator.objects.create(
            username="testuser", phone_number="1234567890"
        )

    def tearDown(self):
        self.user.delete()

    def test_get_coordinator(self):
        # Test the GET method to retrieve a user
        response = self.client.get("/api/getCordinators/{}/".format(self.user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")

    def test_create_coordinator(self):
        # Test the POST method to create a user
        data = {
            "username": "newuser@gmail.com",
            "phone_number": "9876543210",
            "email": "newuser@gmail.com",
            "password": "11111111",
            "firstname": "user",
            "lastname": "name",
        }
        response = self.client.post("/api/cordinator-signup/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "newuser@gmail.com")

    def test_update_coordinator(self):
        # Test the PUT method to update a user
        data = {"username": "updateduser", "phone_number": "5555555555"}
        response = self.client.put(
            "/api/coordinator/{}".format(int(self.user.id)), data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "updateduser")
        self.assertEqual(response.data["phone_number"], "5555555555")


class EventTypeAPITestcase(APITestCase):
    def setUp(self):
        self.catergory = EventType.objects.create(
            name="testuser", description="dfksdjfljsd"
        )

    def tearDown(self):
        self.catergory.delete()

    def test_get_category(self):
        response = self.client.get(
            "/api/getCategories/{}".format(int(self.catergory.id))
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "testuser")

    def test_create_category(self):
        data = {"name": "testcategory", "description": "testdescripton"}
        response = self.client.post("/api/getCategories/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "testcategory")

    def test_update_category(self):
        data = {"name": "testcategory1", "description": "testdescripton1"}
        response = self.client.put(
            "/api/getCategories/{}".format(int(self.catergory.id)), data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "testcategory1")
        self.assertEqual(response.data["description"], "testdescripton1")


class EventCoordinatorAPITestcase(APITestCase):
    def setUp(self):
        self.event_type = EventType.objects.create(
            name="testeventtype", description="Test event type description"
        )
        self.event = Event.objects.create(name="testevent", type=self.event_type)
        self.coordinator = Coordinator.objects.create(
            username="testcoordinator",
            email="testcoordinator@test.com",
            approved=True,
            phone_number="1234567890",
            imageUrl="test_image.jpg",
            password="testpassword",
            is_active=True,
        )
        self.event_coordinator = EventCoordinator.objects.create(
            event=self.event,
            coordinator=self.coordinator,
            capacity=10,
            price=100.0,
            is_active=True,
            location="testlocation",
            imageUrl="test_image.jpg",
            description="Test event coordinator description",
        )

    def tearDown(self):
        self.event_coordinator.delete()
        self.event.delete()
        self.event_type.delete()
        self.coordinator.delete()

    def test_get_event_coordinator(self):
        url = reverse(
            "event_coordinator_detail_with_id", args=[self.event_coordinator.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_event_coordinator(self):
        url = reverse("create_event_coordinator")
        data = {
            "event": self.event.id,
            "coordinator": self.coordinator.id,
            "capacity": 20,
            "price": 200.0,
            "is_active": True,
            "location": "newlocation",
            "imageUrl": "new_image.jpg",
            "description": "New event coordinator description",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_event_coordinator(self):
        url = reverse(
            "event_coordinator_detail_with_id", args=[self.event_coordinator.id]
        )
        data = {
            "updatedData": {  # Nest the data under the 'updatedData' key
                "event": self.event.id,
                "coordinator": self.coordinator.id,
                "capacity": 20,
                "price": 200.0,
                "is_active": True,
                "location": "newlocation",
                "imageUrl": "updated_image.jpg",
                "description": "New event coordinator description",
            }
        }
        response = self.client.put(url, data, format="json")  # Use format='json'
        print(response)
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )  # Update expected status code
        self.assertEqual(response.data["event"]["id"], self.event.id)
        self.assertEqual(response.data["coordinator"]["id"], self.coordinator.id)
        self.assertEqual(response.data["capacity"], 20)
        self.assertEqual(response.data["price"], "200.00")
        self.assertEqual(response.data["is_active"], True)
        self.assertEqual(response.data["location"], "newlocation")
        self.assertEqual(response.data["imageUrl"], "updated_image.jpg")
        self.assertEqual(
            response.data["description"], "New event coordinator description"
        )


class VendersAPITestCase(APITestCase):
    def setUp(self):
        self.user = Venders.objects.create(
            username="testuser", phone_number="1234567890"
        )

    def tearDown(self):
        self.user.delete()

    def test_get_Venders(self):
        # Test the GET method to retrieve a user
        response = self.client.get("/api/venders/{}".format(self.user.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")

    def test_create_Venders(self):
        # Test the POST method to create a user
        data = {
            "username": "newuser@gmail.com",
            "phone_number": "9876543210",
            "email": "newuser@gmail.com",
            "password": "11111111",
            "firstname": "user",
            "lastname": "name",
        }
        response = self.client.post("/api/vender-signup/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "newuser@gmail.com")

    def test_update_Venders(self):
        # Test the PUT method to update a user
        data = {"username": "updateduser", "phone_number": "5555555555"}
        response = self.client.put("/api/venders/{}".format(int(self.user.id)), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "updateduser")
        self.assertEqual(response.data["phone_number"], "5555555555")


class ItemAPITestCase(APITestCase):
    def setUp(self):
        # Create a test item
        self.item = Item.objects.create(
            name="Test Item",
            imageUrl="http://example.com/image.jpg",
            description="Test description",
            supplier=None,
            item_type="Car",
            available=True,
            price=10.0,
            quantity=5,
        )
        self.vender = Venders.objects.create(
            username="testvender",
            email="testvender@test.com",
            approved=True,
            phone_number="1234567890",
            imageUrl="test_image.jpg",
            password="testpassword",
            is_active=True,
        )

    def test_get_item_list(self):
        # Retrieve the item list
        url = reverse("getVenders")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_item(self):
        # Define the data for creating a new item
        data = {
            "name": "New Item",
            "imageUrl": "http://example.com/new_image.jpg",
            "description": "New item description",
            "supplier": self.vender.id,
            "item_type": "Car",
            "available": True,
            "price": 20.0,
            "quantity": 10,
        }

        # Create a new item
        url = reverse("create_item")
        response = self.client.post(url, data)

        # Assert that the response status code is 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert that the item was created and its fields match the provided data
        item = Item.objects.get(pk=response.data["id"])
        self.assertEqual(item.name, data["name"])
        self.assertEqual(item.imageUrl, data["imageUrl"])
        self.assertEqual(item.description, data["description"])
        self.assertEqual(item.supplier.id, data["supplier"])
        self.assertEqual(item.item_type, data["item_type"])
        self.assertEqual(item.available, data["available"])
        self.assertEqual(item.price, data["price"])
        self.assertEqual(item.quantity, data["quantity"])


class EventUserBookingAPITestCase(APITestCase):
    def setUp(self):
        self.user = MyUser.objects.create(
            username="testuser", phone_number="1234567890"
        )
        self.event_type = EventType.objects.create(
            name="Conference", description="Conference event type"
        )
        self.event = Event.objects.create(name="Conference Event", type=self.event_type)
        self.coordinator = Coordinator.objects.create(
            username="testcoordinator",
            email="testcoordinator@test.com",
            approved=True,
            phone_number="1234567890",
            imageUrl="test_image.jpg",
            password="testpassword",
            is_active=True,
        )
        self.event_coordinator = EventCoordinator.objects.create(
            event=self.event,
            coordinator=self.coordinator,
            capacity=10,
            price=100.0,
            is_active=True,
            location="testlocation",
            imageUrl="test_image.jpg",
            description="Test event coordinator description",
        )
        self.event_user_book = EventUserBook.objects.create(
            user=self.user, event=self.event_coordinator
        )
        self.url = reverse("events_user_Booking")

    def tearDown(self):
        self.user.delete()
        self.event_type.delete()
        self.event.delete()
        self.coordinator.delete()
        self.event_user_book.delete()

    def test_create_event_user_book(self):
        data = {
            "user": self.user.username,
            "event": self.event_coordinator.pk,
            "selectedDatefrom": "2023-06-19T18:30:00.000Z",
            "selectedDateto": "2023-06-19T18:30:00.000Z",
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        event_user_book = EventUserBook.objects.get(pk=response.data["id"])
        serializer = EventUserBookSerializer(event_user_book)
        self.assertEqual(response.data, serializer.data)

    def test_get_event_user_book(self):
        detail_url = reverse(
            "event-user-book-detail", kwargs={"pk": self.event_user_book.pk}
        )
        response = self.client.get(detail_url)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
