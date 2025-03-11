from django.urls import path
from .views import HomeView, AccountView, AccountDetailsView

urlpatterns = [
    path('', HomeView, name='home'),

    path('accounts/get/', AccountView, name='accounts'),
    path('account/<str:pk>/', AccountDetailsView, name='account'),
]
