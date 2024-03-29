# Aplikacja powinna mieć co najmniej jeden widok dostępny
# tylko dla zalogowanego użytkownika (używając Django Auth system).
from pyexpat.errors import messages
from django.shortcuts import render, redirect
from Pet_walking.models import Owner, Walker, Pet, Request, SIZES, User
from django.views import View
from .forms import WalkerSignUpForm, OwnerSignUpForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.generic import CreateView
from Pet_walking.forms import Requests


class HomeView(View):
    """
    Displays the home page of the website.
    """
    def get(self, request):
        return render(request, 'home.html')


class Registration(View):
    """
    Displays the registration page of the website where a person can
    choose the type of user under which wants to enter the page.
    """
    def get(self, request):
        return render(request, 'registration.html')


class OwnerRegistration(CreateView):
    """
    Handles the registration process for owners.
    """
    model = User
    form_class = OwnerSignUpForm
    template_name = 'add_owner.html'

    def form_valid(self, form):
        request = self.request
        user = form.save()
        phone_number = form.cleaned_data['phone_number']
        city = form.cleaned_data['city']
        number_of_flat = form.cleaned_data['number_of_flat']
        street = form.cleaned_data['street']
        owner = Owner(user=user, city=city, street=street, number_of_flat=number_of_flat, phone_number=phone_number)
        check_phone_number = Owner.objects.filter(phone_number=phone_number)
        if check_phone_number:
            message = messages.error(request, "This phone number already exists. Try again!")
            return render(request, 'wrong_number_message.html', {'message': message})
        else:
            owner.save()
            login(request, user)
            return redirect('home')


class WalkerRegistration(CreateView):
    """
    Handles the registration process for walkers.
    """
    model = User
    form_class = WalkerSignUpForm
    template_name = 'add_walker.html'

    def form_valid(self, form):
        user = form.save()
        phone_number = form.cleaned_data['phone_number']
        walker = Walker(user=user, phone_number=phone_number)
        walker.save()
        login(self.request, user)
        return redirect('home')


class LoginView(View):
    """
    Displays the login page and handles user authentication.
    """
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})

    def post(self, http_request):
        username = http_request.POST['username']
        password = http_request.POST['password']
        user = authenticate(http_request, username=username, password=password)
        if user is not None:
            login(http_request, user)
            if hasattr(user, 'owner'):
                http_request.session['user_type'] = 'owner'
                http_request.session['user_id'] = user.owner.id
            elif hasattr(user, 'walker'):
                http_request.session['user_type'] = 'walker'
                http_request.session['user_id'] = user.walker.id
            # Redirect the user to the home page
            message = messages.error(http_request, f"Hello, {user.username}!")
            return render(http_request, 'hello_message.html', {'message': message})
        else:
            # Return an error message to the user
            message = messages.error(http_request, f"Wrong credentials!")
            return render(http_request, 'wrong_credentials.html', {'message': message})


class LogoutView(View):
    """
    View responsible for logging out the user.
    """
    def get(self, request):
        logout(request)
        request.session.delete()
        message = messages.error(request, f"Goodbye!")
        return render(request, 'bye_message.html', {'message': message})


class AddPetView(View):
    """
    View responsible for adding a pet to the user's list of pets.
    """
    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
            pets = Pet.objects.filter(owner=user).order_by("nickname")
            return render(request, 'add_pet.html', {'pets': pets, 'sizes': SIZES})
        else:
            message = messages.error(request, "You must be logged in to add a pet.")
            return render(request, 'messages.html', {'message': message})

    def post(self, request):
        if request.user.is_authenticated:
            user = request.user
            pets = Pet.objects.filter(owner=user).order_by("nickname")
            nickname = request.POST['nickname']
            breed = request.POST['breed']
            description = request.POST['description']
            size = request.POST['size']
            check_nickname = Pet.objects.filter(nickname=nickname)
            if check_nickname:
                message = messages.error(request, "Dog with this nickname already exists.")
                return render(request, 'message_for_add_pet.html', {'message': message})
            else:
                Pet.objects.create(nickname=nickname, breed=breed, description=description, size=size, owner=user)
                message = messages.success(request, 'Your pet was successfully added!')
                return render(request, 'messages.html',
                              {'message': message, 'pets': pets, 'sizes': SIZES})
        else:
            message = messages.error(request, "You must be logged in to add a pet.")
            return render(request, 'messages.html', {'message': message})


class MyPetsView(View):
    """
    View responsible for displaying the list of pets belonging to the currently logged in user.
    """
    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
            pets = Pet.objects.filter(owner=user).order_by("nickname")
            return render(request, 'my_pets_view.html', {'pets': pets, 'sizes': SIZES})
        else:
            message = messages.error(request, "You must be logged in to see your pets.")
            return render(request, 'messages.html', {'message': message})


class CreateRequestView(View):
    """
    A view that handles creating a new request for a pet
    and displays a list of requests that was added by the user.
    """
    def get(self, http_request):
        if http_request.user.is_owner:
            pets = Pet.objects.filter(owner=http_request.user)
        else:
            pets = Pet.objects.all()
        return render(http_request, 'create_request.html', {'pets': pets})

    def post(self, http_request):
        date = http_request.POST['date']
        pet_id = http_request.POST['pet']
        price = http_request.POST['price']
        duration = http_request.POST['duration']
        pet = Pet.objects.get(id=pet_id)
        Request.objects.create(date=date, pet=pet, price=price, duration=duration)
        message = messages.success(http_request, 'Your request was successfully created!')
        return render(http_request, 'messages_requests.html', {'message': message, 'pet': pet})


class OwnerRequestsView(View):
    """
    A view that displays a list of the requests associated with the owner's pets.
    """
    def get(self, http_request):
        if http_request.user.is_owner:
            pets = Pet.objects.filter(owner=http_request.user)
            requests = Request.objects.filter(pet__in=pets)
        else:
            pets = Pet.objects.all()
            requests = Request.objects.all()
        return render(http_request, 'owner_requests_view.html', {'pets': pets, 'requests': requests})


class AllCreatedRequests(View):
    """
    A view that displays a list of all created requests and available only for walkers.
    """
    def get(self, http_request):
        if http_request.user.is_owner:
            pets = Pet.objects.filter(owner=http_request.user).order_by("nickname")
            requests = Request.objects.filter(pet__in=pets)
        else:
            pets = Pet.objects.all()
            requests = Request.objects.all()
        return render(http_request, 'all_created_requests.html',
                      {'pets': pets, 'requests': requests})

    def post(self, http_request):
        form = Requests(http_request.POST)
        if form.is_valid():
            # new_status = form.cleaned_data['available_for_booking']
            selected_requests = http_request.POST.getlist('request')
            for request_id in selected_requests:
                request = Request.objects.get(id=request_id)
                # new_status = request.POST.get('available_for_booking', True) == False
                request.available_for_booking = False
                request.walker = http_request.user
                request.save()
            message = messages.success(http_request, 'You successfully reserved a walk!')
            return render(http_request, 'walker_message.html', {'message': message, 'form': form})


class SelectedRequests(View):
    """
    It retrieves and displays requests assigned to a walker that is currently logged in.
    """
    def get(self, request):
        if request.user.is_authenticated:
            requests = Request.objects.filter(walker=request.user)
            return render(request, 'selected_requests.html', {'requests': requests})
        else:
            message = messages.error(request, "You must be logged in to see your requests.")
            return render(request, 'walker_message.html', {'message': message})
