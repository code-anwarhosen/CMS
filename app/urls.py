from django.urls import path

from .views import LoginView, LogoutView, SignUpView
from .views import ( HomeView, GetAccounts, AccountDetailsView, CreateAccountForm, 
    CreateAccount, GetPreCreationData, CreateCustomer, CreateGuarantor, CreatePayment )

urlpatterns = [
    path('user/login/', LoginView, name='login'),
    path('user/logout/', LogoutView, name='logout'),
    path('user/sign-up/', SignUpView, name='sign-up'),
    path('', HomeView, name='home'),

    path('accounts/get/', GetAccounts),
    path('account/get/<str:pk>/', AccountDetailsView, name='account'),
    # path('account/get/<str:pk>/make-payment/', CreatePayment),

    path('account/new/', CreateAccountForm, name='create-account'),
    path('account-precreation/data/', GetPreCreationData),
    path('account/create/', CreateAccount),

    path('customer/create/', CreateCustomer),
    path('guarantor/create/', CreateGuarantor),
]
