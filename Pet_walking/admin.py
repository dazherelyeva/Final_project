from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from Pet_walking.models import Owner, Walker, Request, Pet, User
# Register your models here.

admin.site.register(Owner) #UserAdmin
admin.site.register(Walker)
admin.site.register(Request)
admin.site.register(Pet)
admin.site.register(User)
