from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser, User


class User(AbstractUser):
    """
    A custom user model that allows for both owners and walkers.

    Attributes:
        is_owner (bool): Whether the user is an owner.
        is_walker (bool): Whether the user is a walker.
        first_name (str): The user's first name.
        last_name (str): The user's last name.
    """
    is_owner = models.BooleanField(default=False)
    is_walker = models.BooleanField(default=False)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)


class Owner(models.Model):
    """
    A model representing an owner who has one-to-one relationship with a user model
    and his/her attributes(address and owner's pets and requests).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='walker', null=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    street = models.CharField(max_length=255, null=True, blank=True)
    number_of_flat = models.CharField(max_length=255, null=True, blank=True)
    phone_number = PhoneNumberField(null=False, blank=False,
                                    unique=True, help_text='Phone number')
    pets = models.ForeignKey('Pet', on_delete=models.CASCADE, related_name='pets', null=True)
    requests = models.ForeignKey('Request', on_delete=models.CASCADE, related_name='request', null=True)

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to set is_owner and is_walker fields of the User model.
        """
        if self.user:
            self.user.is_owner = True
            self.user.is_walker = False
            self.user.save()
        super().save(*args, **kwargs)


SIZES = (
    (0, 'n/a'),
    (1, 'small'),
    (2, 'medium'),
    (3, 'big')
)


class Pet(models.Model):
    """
    A model representing owner's pet and his/her attributes.
    """
    nickname = models.CharField(max_length=64, unique=True)
    breed = models.CharField(max_length=100)
    description = models.TextField()
    size = models.IntegerField(choices=SIZES, default=0)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        """
        Returns a string representation of the pet's nickname.
        """
        return self.nickname


class Walker(models.Model):
    """
    A model representing a walker who has one-to-one relationship with a user model
    and his/her attributes(phone number and pets with which can reserve a walk).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE,  related_name='owner', null=True)
    phone_number = PhoneNumberField(null=False, blank=False,
                                    unique=True, help_text='Phone number')
    pets = models.ManyToManyField('Pet', related_name='walkers')

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to set is_owner and is_walker fields of the User model.
        """
        if self.user:
            self.user.is_owner = False
            self.user.is_walker = True
            self.user.save()
        super().save(*args, **kwargs)


class Request(models.Model):
    """
    A model representing a pet walking request with attributes(walker who respond on this request)
    """
    date = models.DateField()
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='pet')
    price = models.IntegerField(null=True)
    duration = models.PositiveIntegerField(default=None)
    available_for_booking = models.BooleanField(default=True)
    walker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='walkers', null=True)

    class Meta:
        unique_together = ('pet', 'date')
