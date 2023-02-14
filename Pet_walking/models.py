from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser, User


class User(AbstractUser):
    is_owner = models.BooleanField(default=False)
    is_walker = models.BooleanField(default=False)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)


class Owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='walker', null=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    street = models.CharField(max_length=255, null=True, blank=True)
    number_of_flat = models.CharField(max_length=255, null=True, blank=True)
    phone_number = PhoneNumberField(null=False, blank=False,
                                    unique=True, help_text='Phone number')
    pets = models.ForeignKey('Pet', on_delete=models.CASCADE, related_name='pets', null=True)
    requests = models.ForeignKey('Request', on_delete=models.CASCADE, related_name='request', null=True)


    def save(self, *args, **kwargs):
        if self.user:
            self.user.is_owner = True
            self.user.is_walker = False
            self.user.save()
            # self.name = self.user.username
        super().save(*args, **kwargs)

SIZES = (
    (0, 'n/a'),
    (1, 'small'),
    (2, 'medium'),
    (3, 'big')
)

class Pet(models.Model):
    nickname = models.CharField(max_length=64, unique=True)
    breed = models.CharField(max_length=100)
    description = models.TextField()
    size = models.IntegerField(choices=SIZES, default=0)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


    # tworzymy relacje jeden do wielu: 1 owner moze miec wielu psy
    # What does Related_name mean in Django?
    # The related_name attribute specifies the name of the reverse relation from the User model back to your model.
    # If you don't specify a related_name, Django automatically creates one using the name of your model with the suffix _set.

    def __str__(self):
        return self.nickname

class Walker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,  related_name='owner', null=True)
    phone_number = PhoneNumberField(null=False, blank=False,
                                    unique=True, help_text='Phone number')
    pets = models.ManyToManyField('Pet', related_name='walkers')

    def save(self, *args, **kwargs):
        if self.user:
            self.user.is_owner = False
            self.user.is_walker = True
            self.user.save()
        #     self.name = self.user.username
        super().save(*args, **kwargs)

#     def __str__(self):
#         return self.username.username
# return self.user.username
# jeśli chcemy, żeby ten element był bardziej opisowy,
# powinniśmy zmodyfikować model, nadpisując magiczną metodę __str__ tak, aby np. zwracała ona nazwę


class Request(models.Model):
    date = models.DateField()
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='pet')
    price = models.IntegerField(null=True)
    duration = models.PositiveIntegerField(default=None)
    available_for_booking = models.BooleanField(default=True)
    walker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='walkers', null=True)

    class Meta:
        unique_together = ('pet', 'date')
