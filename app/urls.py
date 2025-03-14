from django.urls import path

from .views import LoginView, LogoutView, SignUpView
from .views import ( HomeView, GetAccounts, AccountDetailsView,
    CreateAccount, GetPreCreationData, CreateCustomer )

urlpatterns = [
    path('user/login/', LoginView, name='login'),
    path('user/logout/', LogoutView, name='logout'),
    path('user/sign-up/', SignUpView, name='sign-up'),
    path('', HomeView, name='home'),

    path('accounts/get/', GetAccounts, name='accounts'),
    path('account/get/<str:pk>/', AccountDetailsView, name='account'),
    path('account/new/', CreateAccount, name='create-account'),
    path('account-precreation/data/', GetPreCreationData, name='get-precreation-data'),

    path('customer/create/', CreateCustomer, name='create-customer'),
]
