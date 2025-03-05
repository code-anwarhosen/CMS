from django.urls import path
from .views import HomeView, CustomerView

urlpatterns = [
    path('', HomeView, name='home'),

    path('customer/get/', CustomerView, name='customers'),
]
