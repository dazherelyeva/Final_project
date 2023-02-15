"""My_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from Pet_walking import views
from django.views.generic import TemplateView

urlpatterns = [
    path('home/', views.HomeView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('abou_us/', TemplateView.as_view(template_name='about_us.html'), name='about_us'),
    path('registration/', views.Registration.as_view(), name='registration'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('add_owner/', views.OwnerRegistration.as_view(), name='add_owner'),
    path('add_walker/', views.WalkerRegistration.as_view(), name='add_walker'),
    path('add_pet/', views.AddPetView.as_view(), name='add_pet'),
    path('my_pets_view/', views.MyPetsView.as_view(), name='my_pets_view'),
    path('create_request/', views.CreateRequestView.as_view(), name='create_request'),
    path('owner_requests_view/', views.OwnerRequestsView.as_view(), name='owner_requests_view'),
    path('all_created_requests/', views.AllCreatedRequests.as_view(), name='all_created_requests'),
    path('selected_requests/', views.SelectedRequests.as_view(), name='selected_requests'),
]
