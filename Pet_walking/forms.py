from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from .models import Owner, User, Walker


class OwnerSignUpForm(UserCreationForm):
    """
    A form for signing up an owner, extending Django's UserCreationForm with additional required
     fields for first name, last name, city, street, number of flat, and phone number.
    """
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    city = forms.CharField(required=True)
    street = forms.CharField(required=True)
    number_of_flat = forms.CharField(required=True)
    phone_number = forms.CharField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def data_save(self):
        """
        Save the owner's data and create an Owner object.
        :return:  The saved user object.
        """
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.is_owner = True
        user.save()
        owner = Owner.objects.create(user=user)
        owner.city = self.cleaned_data.get('city')
        owner.street = self.cleaned_data.get('street')
        owner.number_of_flat = self.cleaned_data.get('number_of_flat')
        owner.phone_number = self.cleaned_data.get('phone_number')
        owner.save()
        return user


class WalkerSignUpForm(UserCreationForm):
    """
    A form for signing up a walker, extending Django's UserCreationForm with
     additional required fields for first name, last name, and phone number.
    """
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_number = forms.CharField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def data_save(self):
        """
        Save the walker's data and create a Walker object.
        :return: The saved user object.
        """
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.is_walker = True
        user.save()
        walker = Walker.objects.create(user=user)
        walker.phone_number = self.cleaned_data.get('phone_number')
        walker.save()
        return user


class Requests(forms.Form):
    """
    A form with a single boolean field for marking a walker as available for booking requests.
    """
    available_for_booking = forms.BooleanField(label='Available for Booking', required=False)
