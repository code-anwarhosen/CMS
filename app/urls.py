from django.urls import path

from .views import LoginView, LogoutView, SignUpView
from .views import HomeView, AccountView, AccountDetailsView

urlpatterns = [
    path('user/login/', LoginView, name='login'),
    path('user/logout/', LogoutView, name='logout'),
    path('user/sign-up/', SignUpView, name='sign-up'),
    path('', HomeView, name='home'),

    path('accounts/get/', AccountView, name='accounts'),
    path('account/<str:pk>/', AccountDetailsView, name='account'),
]
