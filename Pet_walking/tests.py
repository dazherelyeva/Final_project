from datetime import datetime
from django.urls import reverse, resolve
from Pet_walking.models import User, Pet, Request
from django.test import Client, TestCase
import pytest


class LoginViewTestCase(TestCase):
    def test_detail_login(self):
        path = reverse('login')
        assert resolve(path).view_name == 'login'

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')

    def test_login_view_success(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello')

    def test_login_view_failure(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Wrong credentials!')

    def test_logout_view_success(self):
        self.client.login(username='testuser', password='testpass')
        # Make a GET request to the logout url
        response = self.client.get(self.logout_url)
        # Assert that the response status code is 200
        self.assertEqual(response.status_code, 200)
        # Assert that the user is redirected to the login page
        self.assertContains(response, 'Goodbye!')
        # Assert that the user is no longer authenticated
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class OwnerViewTest(TestCase):
    def test_owner_view_template_contains(self):
        response = self.client.get(reverse('add_owner'))
        self.assertContains(response, "Owner registration form:")
        self.assertNotContains(response, "Logowanie")

    def test_owner_view_url(self):
        path = reverse('add_owner')
        assert resolve(path).view_name == 'add_owner'


class WalkerViewTest(TestCase):
    def test_owner_view_template_contains(self):
        response = self.client.get(reverse('add_walker'))
        self.assertContains(response, "Walker registration form")
        self.assertNotContains(response, "Logowanie")

    def test_owner_view_url(self):
        path = reverse('add_walker')
        assert resolve(path).view_name == 'add_walker'


@pytest.mark.django_db
class TestAddPetView():

    @pytest.fixture
    def user(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        return user

    def test_get_add_pet_authenticated(self, client, user):
        client.force_login(user)
        url = reverse('add_pet')
        response = client.get(url)
        assert response.status_code == 200
        assert b'Add your dog' in response.content

    def test_get_add_pet_unauthenticated(self, client):
        url = reverse('add_pet')
        response = client.get(url)
        assert response.status_code == 200
        assert b'You must be logged in to add a pet.' in response.content


class MyPetsViewTest(TestCase):
    def test_detail_my_pets_view(self):
        path = reverse('my_pets_view')
        assert resolve(path).view_name == 'my_pets_view'

    def setUp(self):
        # Create a test user and some test pets
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.pet1 = Pet.objects.create(nickname='Fido', breed='Akita', owner=self.user)
        self.pet2 = Pet.objects.create(nickname='Garfield', breed='Beagle', owner=self.user)
        self.pet3 = Pet.objects.create(nickname='Tweety', breed='Husky', owner=self.user)

        self.client = Client()
        self.client.login(username='testuser', password='testpass')

    def test_get_my_pets(self):
        url = reverse('my_pets_view')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.pet1.nickname)
        self.assertContains(response, self.pet1.breed)
        self.assertContains(response, self.pet2.nickname)
        self.assertContains(response, self.pet2.breed)
        self.assertContains(response, self.pet3.nickname)
        self.assertContains(response, self.pet3.breed)

        # Check that only pets belonging to the logged-in user are displayed
        self.assertNotContains(response, 'Sylvester')
        self.assertNotContains(response, 'Boxer')

        #     'pet': self.pet.id,
        #     'price': self.price,
        #     'duration': self.duration,
        # }
        # response = self.client.post(reverse('create_request'), data)
        # self.assertEqual(response.status_code, 200)
        # assert Request.objects.count() == 1
        # request = Request.objects.first()
        # self.assertEqual(request.date, self.date)
        # self.assertEqual(request.pet, self.pet)
        # self.assertEqual(request.price, self.price)
        # self.assertEqual(request.duration, self.duration)

    def test_create_request_unique_date(self):
        # Create a request with a known date
        self.existing_date_str = '2023-03-03'
        self.existing_date = datetime.strptime(self.existing_date_str, '%Y-%m-%d').date()

        self.client.force_login(self.user)
        data = {
            'date': self.existing_date,
            'pet': self.pet.id,
            'price': self.price,
            'duration': self.duration,
        }
        response = self.client.post(reverse('create_request'), data)
        self.assertEqual(response.status_code, 200)
        assert Request.objects.count() < 2


class OwnerRequestsViewTest(TestCase):
    def setUp(self):
        # Create a test user and some test pets
        self.user1 = User.objects.create_user(username='testuser1', password='testpass1')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass2')
        self.pet1 = Pet.objects.create(nickname='Fido', breed='Akita', owner=self.user1)
        self.pet2 = Pet.objects.create(nickname='Garfield', breed='Beagle', owner=self.user2)
        self.request1 = Request.objects.create(pet=self.pet1, date='2023-03-03', price=30, duration=1)
        self.request2 = Request.objects.create(pet=self.pet1, date='2024-03-03', price=100, duration=5)

        self.client = Client()
        self.client.login(username='testuser1', password='testpass1')

    def test_get_my_requests(self):
        url = reverse('owner_requests_view')
        response = self.client.get(url)

        # Check that the response contains only the user's pets and requests
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.pet1.nickname)
        self.assertContains(response, self.request1.pet)
        self.assertContains(response, self.request2.pet)

        # Check that only pets belonging to the logged-in user are displayed
        self.assertNotContains(response, 'request3')
        self.assertNotContains(response, 'request4')


class RegistrationTest(TestCase):
    def test_registration_template_contains(self):
        response = self.client.get(reverse('registration'))
        self.assertContains(response, "Choose an option:")
        self.assertNotContains(response, "Logowanie")

    def test_detail_sign_up(self):
        path = reverse('registration')
        assert resolve(path).view_name == 'registration'


class HomeViewTest(TestCase):
    def test_detail_home(self):
        path = reverse('home')
        assert resolve(path).view_name == 'home'

    def test_home_template_contains(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, "")
        self.assertNotContains(response, "Home")


class AllRequestViewTest(TestCase):
    def setUp(self):
        self.owner_user = User.objects.create_user(username='owner', password='testpassword', is_owner=True)
        self.walker_user = User.objects.create_user(username='walker', password='testpassword', is_owner=False)

        self.pet1 = Pet.objects.create(owner=self.owner_user, nickname='Max', breed='Akita')
        self.pet2 = Pet.objects.create(owner=self.owner_user, nickname='Mittens', breed='Akita')

        self.request1 = Request.objects.create(pet=self.pet1, date='2022-04-12', price=30, duration=1)
        self.request2 = Request.objects.create(pet=self.pet2, date='2022-04-13', price=30, duration=1)

        self.client.login(username='walker', password='testpassword')

    def test_get(self):
        url = reverse('all_created_requests')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'all_created_requests.html')
        self.assertEqual(len(response.context['pets']), 2)
        self.assertEqual(len(response.context['requests']), 2)

    def test_post(self):
        url = reverse('all_created_requests')
        data = {'request': [self.request1.id]}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'walker_message.html')
        self.assertContains(response, 'You successfully reserved a walk!')
        self.assertFalse(Request.objects.get(id=self.request1.id).available_for_booking)
        self.assertEqual(Request.objects.get(id=self.request1.id).walker, self.walker_user)


class SelectedRequestsTest(TestCase):
    def setUp(self):
        self.owner_user = User.objects.create_user(username='owner', password='testpassword', is_owner=True)
        self.walker_user = User.objects.create_user(username='walker', password='testpassword', is_owner=False)

        self.pet1 = Pet.objects.create(owner=self.owner_user, nickname='Max', breed='Akita')
        self.pet2 = Pet.objects.create(owner=self.owner_user, nickname='Mittens', breed='Akita')

        self.request1 = Request.objects.create(walker=self.walker_user, pet=self.pet1,
                                               date='2023-05-13', price=30, duration=1)
        self.request2 = Request.objects.create(walker=self.walker_user, pet=self.pet1,
                                               date='2023-04-13', price=30, duration=1)

        self.other_request = Request.objects.create(pet_id=2, date='2023-05-13', price=70, duration=1)

    def test_get_with_authenticated_user(self):
        self.client.login(username='walker', password='testpassword')
        url = reverse('selected_requests')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'selected_requests.html')
        self.assertEqual(len(response.context['requests']), 2)

    def test_get_with_unauthenticated_user(self):
        url = reverse('selected_requests')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'walker_message.html')
        self.assertContains(response, 'You must be logged in to see your requests.')
