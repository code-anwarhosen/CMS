from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json

from .models import ( Account, Customer, Guarantor, 
    Product, Model, Contract, Payment, PRODUCT_CATEGORIES, OCCUPATIONS )
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
def CreateAccountForm(request):

    occupationOptions = [{
        'value': occu[0],
        'name': occu[1]
    } for occu in OCCUPATIONS]

    context = {
        'occupationOptions': occupationOptions
    }
    return render(request, 'pages/accountCreationForm.html', context)




@login_required
def GetPreCreationData(request):
    user = request.user

    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
    
    try:
        # Fetch customers and serialize
        customers = user.customers.all()
        serialized_customers = [
            {
                'uid': customer.uid,
                'name': customer.name,
                'phone': customer.phone,
                'address': customer.address,
                'occupation': customer.occupation
            }
            for customer in customers
        ]

        # Fetch guarantors and serialize
        guarantors = user.guarantors.all()
        serialized_guarantors = [
            {
                'uid': guarantor.uid,
                'name': guarantor.name,
                'phone': guarantor.phone,
                'address': guarantor.address,
                'occupation': guarantor.occupation
            }
            for guarantor in guarantors
        ]

        # Prepare product categories
        categories = [
            {'value': category[0], 'name': category[1]}
            for category in PRODUCT_CATEGORIES
        ]

        # Fetch products and serialize
        products = Product.objects.select_related('model').all()
        serialized_products = [
            {
                'category': product.category,
                'model': product.model.name
            }
            for product in products
        ]

        # Prepare response data
        data = {
            'customers': serialized_customers,
            'guarantors': serialized_guarantors,
            'productCategories': categories,
            'products': serialized_products,
        }

        return JsonResponse({'success': True, 'data': data})

    except Exception as e:
        return JsonResponse({'success': False, 'message': 'An error occurred while fetching data.'}, status=500)



@login_required
def CreateCustomer(request):
    user = request.user

    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

    try:
        # Parse JSON data
        data = json.loads(request.body)

        # Extract fields
        name = data.get('fullname')
        phone = data.get('phone')
        address = data.get('address')

        # Validate required fields
        if not name or not phone or not address:
            return JsonResponse({'status': 'error', 'message': 'Full Name, Phone, and Address are required fields.'}, status=400)

        # Check if customer already exists with the given phone number
        customer = Customer.objects.filter(phone=phone).first()
        if customer:
            response_data = {
                'uid': customer.uid,
                'name': customer.name,
                'phone': customer.phone,
                'address': customer.address,
                'occupation': customer.occupation
            }
            return JsonResponse({
                'status': 'success',
                'message': f'Customer already exists with this phone number. UID: {customer.uid}',
                'customer': response_data
            }, status=200)

        # Extract optional fields
        age = data.get('age')
        occupation = data.get('occupation')
        location_mark = data.get('locationMark')
        guardian_type = data.get('guardianType')
        guardian_name = data.get('guardianName')

        # Create new customer
        customer = Customer.objects.create(
            creator=user,
            name=name,
            phone=phone,
            address=address,
            occupation=occupation,
            locationMark=location_mark,
            guardianType=guardian_type,
            guardianName=guardian_name
        )

        # Set age if provided
        if age:
            customer.age = int(age)
            customer.save()  # Save again to update age

        # Prepare response data
        response_data = {
            'uid': customer.uid,
            'name': customer.name,
            'phone': customer.phone,
            'address': customer.address,
            'occupation': customer.occupation,
            'age': customer.age,
            'locationMark': customer.locationMark,
            'guardianType': customer.guardianType,
            'guardianName': customer.guardianName
        }

        return JsonResponse({
            'status': 'success',
            'message': 'Customer created successfully!',
            'customer': response_data
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)

    except ValueError as e:
        return JsonResponse({'status': 'error', 'message': 'Invalid value for age.'}, status=400)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'An error occurred while creating the customer.'}, status=500)



@login_required
def CreateGuarantor(request):
    user = request.user

    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

    try:
        # Parse JSON data
        data = json.loads(request.body)

        # Extract fields
        name = data.get('guarantorName')
        phone = data.get('guarantorPhone')
        address = data.get('guarantorAddress')
        occupation = data.get('guarantorOccupation')

        # Validate required fields
        if not name or not phone:
            return JsonResponse({'status': 'error', 'message': 'Name and Phone are required fields.'}, status=400)

        # Check if guarantor already exists with the given phone number
        guarantor = Guarantor.objects.filter(phone=phone).first()
        if guarantor:
            response_data = {
                'uid': guarantor.uid,
                'name': guarantor.name,
                'phone': guarantor.phone,
                'address': guarantor.address,
                'occupation': guarantor.occupation
            }
            return JsonResponse({
                'status': 'success',
                'message': f'Guarantor already exists with this phone number. UID: {guarantor.uid}',
                'guarantor': response_data
            }, status=200)

        # Create new guarantor
        guarantor = Guarantor.objects.create(
            creator=user,
            name=name,
            phone=phone,
            address=address,
            occupation=occupation
        )

        # Prepare response data
        response_data = {
            'uid': guarantor.uid,
            'name': guarantor.name,
            'phone': guarantor.phone,
            'address': guarantor.address,
            'occupation': guarantor.occupation
        }

        return JsonResponse({
            'status': 'success',
            'message': 'Guarantor created successfully!',
            'guarantor': response_data
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'An error occurred while creating the guarantor.'}, status=500)



@login_required
def CreateAccount(request):
    user = request.user

    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['accountNumber', 'customerUid', 'selectedModel', 'firstGuarantorUid', 
            'secondGuarantorUid', 'cashValue', 'hireValue', 'downPayment', 'monthlyPayment', 'length', 'saleDate']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({'status': 'error', 'message': f'"{field}" is required.'}, status=400)

        account_number = data['accountNumber']
        customer_uid = data['customerUid']
        selected_model = data['selectedModel']
        first_guarantor_uid = data['firstGuarantorUid']
        second_guarantor_uid = data['secondGuarantorUid']

        # Check if account already exists
        if Account.objects.filter(number=account_number).exists():
            return JsonResponse({'status': 'error', 'message': f'An account already exists with this "{account_number}" account number.'}, status=400)

        # Check for customer
        customer = Customer.objects.filter(uid=customer_uid).first()
        if not customer:
            return JsonResponse({'status': 'error', 'message': f'Customer with UID {customer_uid} does not exist.'}, status=404)

        # Check for product
        product_model = Model.objects.filter(name=selected_model).first()
        if not product_model or not product_model.product:
            return JsonResponse({'status': 'error', 'message': 'There is no product associated with the selected model.'}, status=400)
        product = product_model.product

        # Check for guarantors
        first_guarantor = Guarantor.objects.filter(uid=first_guarantor_uid).first()
        second_guarantor = Guarantor.objects.filter(uid=second_guarantor_uid).first()

        if not first_guarantor or not second_guarantor:
            return JsonResponse({'status': 'error', 'message': f'Guarantors with UID {first_guarantor_uid} or {second_guarantor_uid} do not exist.'}, status=404)

        # Create account
        account = Account.objects.create(
            creator=user,
            number=account_number,
            saleDate=data['saleDate'],
            customer=customer,
            product=product
        )
        account.guarantors.add(first_guarantor, second_guarantor)

        # Create contract
        try:
            contract = Contract.objects.create(
                cashValue=int(data['cashValue']),
                hireValue=int(data['hireValue']),
                downPayment=int(data['downPayment']),
                monthlyPayment=int(data['monthlyPayment']),
                length=int(data['length'])
            )
            account.contract = contract
            account.save()
        except Exception as e:
            return JsonResponse({'status': 'success', 'message': 'Account created successfully, but there might be issues with the contract information.'})

        return JsonResponse({
            'status': 'success', 
            'message': 'Account created successfully!', 
            'data': {'accountNumber': account.number
        }})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)
    except Exception as e:
        print('error', e)
        return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred.'}, status=500)



@login_required
def CreatePayment(request, pk):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
    
    contract = Contract.objects.filter(pk=pk).first()
    if not pk or not contract:
        return JsonResponse({'status': 'error', 'message': 'The account you\'re trying to make payment is invalid!'})
    
    try:
        data = json.loads(request.body)
        
        required_fields = ['paymentAmount', 'receiptNumber', 'paymentDate']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({'status': 'error', 'message': f'"{field}" is required.'}, status=400)

        paymentAmount = data['paymentAmount']
        receiptNumber = data['receiptNumber']
        paymentDate = data['paymentDate']
        
        if paymentAmount:
            payment = Payment.objects.create(
                contract=contract,
                paymentDate=paymentDate,
                receiptNumber=receiptNumber,
                paymentAmount=int(paymentAmount)
            )
            return JsonResponse({'status': 'success', 'message': 'Payment created!', 'payment': payment})
        else:
            return JsonResponse({'status': 'error', 'message': 'Payment amount should not be empty.'})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)
    except Exception as e:
        print('error', e)
        return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred.'}, status=500)
