import pytest
from django.contrib.auth.models import User
from django.test import Client
from .models import Pet, Request

@pytest.fixture
def client():
    """Returns a Django test client."""
    return Client()

@pytest.fixture
def pet_factory():
    """Creates and returns a Pet object."""
    def factory(name, owner):
        return Pet.objects.create(name=name, owner=owner)
    return factory

@pytest.fixture
def user():
    """Creates and returns a User object."""
    return User.objects.create_user(username='testuser', password='testpass')

@pytest.fixture
def authenticated_client(client, user):
    """Returns an authenticated Django test client."""
    client.force_login(user)
    return client

@pytest.fixture
def request_factory(pet_factory):
    """Creates and returns a Request object."""
    def factory(date, pet, price, duration):
        return Request.objects.create(date=date, pet=pet, price=price, duration=duration)
    return factory