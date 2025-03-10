from django.urls import path
from .views import HomeView, AccountView

urlpatterns = [
    path('', HomeView, name='home'),

    path('accounts/get/', AccountView, name='accounts'),
]
