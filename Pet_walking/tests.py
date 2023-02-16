from datetime import datetime
from django.urls import reverse, resolve
from Pet_walking.models import User, Pet, Request
from django.test import Client, TestCase
import pytest


class LoginViewTestCase(TestCase):
    def test_detail_login(self):
        """
        Checks that the URL for the login view can be resolved correctly and has a view name of 'login'.
        """
        path = reverse('login')
        assert resolve(path).view_name == 'login'

    def setUp(self):
        """
        Sets up the test case by creating a user with a username and password,
        and defining the login and logout URLs for the client to use.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')

    def test_login_view_success(self):
        """
        Tests that the login view works correctly when valid credentials are provided.
        """
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 200)
        # A status code of 200 is commonly used for successful GET requests,
        # but can be used for any type of successful HTTP request.
        self.assertContains(response, 'Hello')

    def test_login_view_failure(self):
        """
         Tests that the login view works correctly when invalid credentials are provided.
        """
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Wrong credentials!')

    def test_logout_view_success(self):
        """
        Tests that the logout view works correctly.
        """
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
        """
        Checks if the 'add_owner' view returns a response with the expected content.
        """
        response = self.client.get(reverse('add_owner'))
        self.assertContains(response, "Owner registration form:")
        self.assertNotContains(response, "Logowanie")

    def test_owner_view_url(self):
        """
        Checks that the URL for the 'add_owner' view can be resolved correctly and has a view name of 'add_owner'.
        """
        path = reverse('add_owner')
        assert resolve(path).view_name == 'add_owner'


class WalkerViewTest(TestCase):
    def test_owner_view_template_contains(self):
        """
        Checks if the 'add_walker' view returns a response with the expected content.
        """
        response = self.client.get(reverse('add_walker'))
        self.assertContains(response, "Walker registration form")
        self.assertNotContains(response, "Logowanie")

    def test_owner_view_url(self):
        """
        Checks that the URL for the 'add_walker' view can be resolved correctly and has a view name of 'add_walker'.
        """
        path = reverse('add_walker')
        assert resolve(path).view_name == 'add_walker'


@pytest.mark.django_db
class TestAddPetView(TestCase):

    @pytest.fixture
    def user(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        return user

    def test_get_add_pet_authenticated(self, client, user):
        """
        Checks that the 'add_pet' view can be accessed by an authenticated user and returns the expected content.
        """
        client.force_login(user)
        url = reverse('add_pet')
        response = client.get(url)
        assert response.status_code == 200
        assert b'Add your dog' in response.content

    def test_get_add_pet_unauthenticated(self, client):
        """
        Checks that the 'add_pet' view redirects unauthenticated users to the login page and
        displays a message indicating that they need to be logged in to add a pet.
        """
        url = reverse('add_pet')
        response = client.get(url)
        assert response.status_code == 200
        assert b'You must be logged in to add a pet.' in response.content


class MyPetsViewTest(TestCase):
    def test_detail_my_pets_view(self):
        """
        Tests if the view name for my_pets_view URL is correct.
        """
        path = reverse('my_pets_view')
        assert resolve(path).view_name == 'my_pets_view'

    def setUp(self):
        """
        Sets up the test case by creating a user with a username and password,
        and defining his pets.
        """
        # Create a test user and some test pets
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.pet1 = Pet.objects.create(nickname='Fido', breed='Akita', owner=self.user)
        self.pet2 = Pet.objects.create(nickname='Garfield', breed='Beagle', owner=self.user)
        self.pet3 = Pet.objects.create(nickname='Tweety', breed='Husky', owner=self.user)

        self.client = Client()
        self.client.login(username='testuser', password='testpass')

    def test_get_my_pets(self):
        """
        Tests if the view returns the correct HTTP response and displays the user's pets.
        """
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


    def test_create_request_unique_date(self):
        """
        Tests if a new request is created successfully with a unique date
        """
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
        """
        Sets up the test case by creating a user with a username and password, defining his pets
        and requests created for that pets.
        """
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
        """
        The tests ensure that the correct requests are displayed for the logged-in user,
        and that only the user's pets and requests are shown.
        The tests also verify that requests from other users are not displayed.
        """
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
        """
        Checks that the response of the registration view contains the expected
        string "Choose an option:", but not the string "Logowanie".
        """
        response = self.client.get(reverse('registration'))
        self.assertContains(response, "Choose an option:")
        self.assertNotContains(response, "Logowanie")

    def test_detail_sign_up(self):
        """
        Checks that the registration view can be resolved using the name 'registration'.
        """
        path = reverse('registration')
        assert resolve(path).view_name == 'registration'


class HomeViewTest(TestCase):
    def test_detail_home(self):
        """
        Checks that the home view can be resolved using the name 'home'.
        """
        path = reverse('home')
        assert resolve(path).view_name == 'home'

    def test_home_template_contains(self):
        """
        Checks that the response of the home view contains an empty string, but not the string "Home".
        """
        response = self.client.get(reverse('home'))
        self.assertContains(response, "")
        self.assertNotContains(response, "Home")


class AllRequestViewTest(TestCase):
    def setUp(self):
        """
        Sets up the test case by creating a user and walker with a username and password, defining owner's pets
        and requests created for that pets.
        """
        self.owner_user = User.objects.create_user(username='owner', password='testpassword', is_owner=True)
        self.walker_user = User.objects.create_user(username='walker', password='testpassword', is_owner=False)

        self.pet1 = Pet.objects.create(owner=self.owner_user, nickname='Max', breed='Akita')
        self.pet2 = Pet.objects.create(owner=self.owner_user, nickname='Mittens', breed='Akita')

        self.request1 = Request.objects.create(pet=self.pet1, date='2022-04-12', price=30, duration=1)
        self.request2 = Request.objects.create(pet=self.pet2, date='2022-04-13', price=30, duration=1)

        self.client.login(username='walker', password='testpassword')

    def test_get(self):
        """
        Checks if the view returns a 200 status code, uses the correct template,
        and passes the correct data to the context.
        """
        url = reverse('all_created_requests')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'all_created_requests.html')
        self.assertEqual(len(response.context['pets']), 2)
        self.assertEqual(len(response.context['requests']), 2)

    def test_post(self):
        """
        Checks if the view successfully reserves a walk and updates the request object accordingly.
        """
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
        """
        Sets up the test case by creating a user and walker with a username and password, defining owner's pets
        and walker's requests.
        """
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
        """
        Check whether the view correctly displays a list of requests for an authenticated user.
        """
        self.client.login(username='walker', password='testpassword')
        url = reverse('selected_requests')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'selected_requests.html')
        self.assertEqual(len(response.context['requests']), 2)

    def test_get_with_unauthenticated_user(self):
        """
        Check whether it displays an appropriate message for an unauthenticated user.
        """
        url = reverse('selected_requests')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'walker_message.html')
        self.assertContains(response, 'You must be logged in to see your requests.')
