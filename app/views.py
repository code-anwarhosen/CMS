from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import Account, Product, Customer, PRODUCT_CATEGORIES, OCCUPATIONS
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
def GetAccounts(request):
    user = request.user

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



@login_required
def AccountDetailsView(request, pk):
    account = Account.objects.filter(pk=pk).first()

    if not account:
        messages.info(request, 'The account you are trying to access does not exists!')
        return redirect('home')
    return render(request, 'pages/accountDetails.html', {'account': account})



@login_required
def CreateAccount(request):

    occupationOptions = [{
        'value': occu[0],
        'name': occu[1]
    } for occu in OCCUPATIONS]

    context = {
        'occupationOptions': occupationOptions
    }
    return render(request, 'pages/accountCreate/accountCreationForm.html', context)


@login_required
def GetPreCreationData(request):
    user = request.user

    customers = user.customers.all()
    serialized_customers = [{
        'uid': cus.uid,
        'name': cus.name,
        'phone': cus.phone,
        'address': cus.address,
        'occupation': cus.occupation
    } for cus in customers]


    guarantors = user.guarantors.all()
    serialized_guarantors = [{
        'uid': gua.uid,
        'name': gua.name,
        'phone': gua.phone,
        'address': gua.address,
        'occupation': gua.occupation
    } for gua in guarantors]

    for customer in serialized_customers:
        serialized_guarantors.append(customer)

    categories = [{
        'value': cate[0],
        'name': cate[1]
    } for cate in PRODUCT_CATEGORIES]

    products = Product.objects.all()
    serialized_products = [{
        'category': product.category,
        'model': product.model.name
    } for product in products]

    data = {
        'customers': serialized_customers,
        'guarantors': serialized_guarantors,
        'productCategories': categories,
        'products': serialized_products,
    }

    return JsonResponse({'success': True, 'data': data})



from django.views.decorators.csrf import csrf_exempt
import json

@login_required
def CreateCustomer(request):
    user = request.user

    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)

            # Extract data from the JSON payload
            name = data.get('fullname')
            phone = data.get('phone')
            address = data.get('address')

            # Validate required fields
            if not name or not phone or not address:
                return JsonResponse({'status': 'error', 'message': 'Full Name, Phone, and Address are required fields.'}, status=400)


            age = data.get('age')
            occupation = data.get('occupation')
            locationMark = data.get('locationMark')
            guardianType = data.get('guardianType')
            guardianName = data.get('guardianName')

            # Create a new Customer instance
            customer = Customer.objects.create(
                creator=user, name=name, phone=phone, address=address,
                occupation=occupation, locationMark=locationMark,
                guardianType=guardianType, guardianName=guardianName
            )
            if age:
                customer.age = int(age)
            customer.save()

            print(customer)

            data = {
                'uid': customer.uid,
                'name': customer.name,
                'phone': customer.phone,
                'address': customer.address,
                'occupation': customer.occupation
            }
            return JsonResponse({'status': 'success', 'message': 'Customer created successfully!', 'customer': data}, status=201)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An error occurred while creating the customer.'}, status=500)

    else:
        # Return an error for non-POST requests
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)
