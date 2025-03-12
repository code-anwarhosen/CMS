from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Account
from .forms import CustomUserCreationForm

def LoginView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have successfully logged in')
            return redirect('home')
        else:
            messages.error(request, 'Invalid Username or Password!')
    return render(request, 'pages/login.html')

@login_required
def LogoutView(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, 'You have successfully logged out')
    else:
        messages.error(request, 'You are not logged in')
    return redirect('login')

def SignUpView(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
        else:
            messages.error(request, 'Registration failed. Please correct the below errors.')
            for error in form.errors:
                messages.error(request, f'{form.errors[error][0]}')
    
    form = CustomUserCreationForm()
    return render(request, 'pages/sign-up.html', {'form': form})


@login_required
def HomeView(request):
    return render(request, 'pages/home.html')

@login_required
def AccountView(request):
    user = request.user

    if request.method == 'GET':
        accounts = user.accounts.all()
        if not accounts:
            return JsonResponse({'success': False})
        
        serialized_data = [{
            'pk': acc.pk,
            'name': acc.customer.name if acc.customer else "Unknown",
            'phone': acc.customer.phone if acc.customer else "N/A",
            'account': acc.number,
            'balance': acc.contract.cashBalance if acc.contract else 0,
            'avatar': acc.customer.avatar.url if acc.customer else None,
            'status': acc.status,
        } for acc in accounts]
        return JsonResponse({'success': True, 'accounts': serialized_data})
    
    elif request.method == 'POST':
        pass

@login_required
def AccountDetailsView(request, pk):
    account = Account.objects.filter(pk=pk).first()

    if not account:
        messages.info(request, 'The account you are trying to access does not exists!')
        return redirect('home')

    return render(request, 'pages/accountDetails.html', {'account': account})