from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json

from .models import ( Account, Customer, Guarantor, 
    Product, Model, Contract, PRODUCT_CATEGORIES, OCCUPATIONS )
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

            customerObj = Customer.objects.filter(phone=phone).first()
            if customerObj:
                data = {
                    'uid': customerObj.uid,
                    'name': customerObj.name,
                    'phone': customerObj.phone,
                    'address': customerObj.address,
                    'occupation': customerObj.occupation
                }
                return JsonResponse({'status': 'success', 'message': f'Customer already exists with this phone number. UID:{customerObj.uid}', 'customer': data}, status=201)

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




@login_required
def CreateGuarantor(request):
    user = request.user

    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            name = data.get('guarantorName')
            phone = data.get('guarantorPhone')
            address = data.get('guarantorAddress')
            occupation = data.get('guarantorOccupation')

            # Validate required fields
            if not name or not phone:
                return JsonResponse({'status': 'error', 'message': 'Name and Phone are required fields.'}, status=400)
            
            # check if gurantor already with the given phone number
            guarantorObj = Guarantor.objects.filter(phone=phone).first()
            if guarantorObj:
                data = {
                    'uid': guarantorObj.uid,
                    'name': guarantorObj.name,
                    'phone': guarantorObj.phone,
                    'address': guarantorObj.address,
                    'occupation': guarantorObj.occupation
                }
                return JsonResponse({'status': 'success', 'message': f'Guarantor already exists with this phone number. UID:{guarantorObj.uid}', 'guarantor': data}, status=201)


            # create new guarantor
            guarantor = Guarantor.objects.create(creator=user, name=name, phone=phone, address=address, occupation=occupation)
            guarantor.save()

            data = {
                'uid': guarantor.uid,
                'name': guarantor.name,
                'phone': guarantor.phone,
                'address': guarantor.address,
                'occupation': guarantor.occupation
            }
            return JsonResponse({'status': 'success', 'message': 'Guarantor created successfully!', 'guarantor': data})
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An error occurred while creating the guarantor.'}, status=500)

    else:
        # Return an error for non-POST requests
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)



@login_required
def CreateAccount(request):
    user = request.user

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(1)

            print(data)

            # Validate required fields
            required_fields = [
                'accountNumber', 'saleDate', 'customerUid', 
                'firstGuarantorUid', 'secondGuarantorUid', 'selectedModel',
                'cashValue', 'hireValue', 'downPayment', 'monthlyPayment', 'length'

            ]

            print(2)
            # for field in required_fields:
            #     if field not in data or not data[field]:
            #         return JsonResponse({'status': 'error', 'message': f'{field} is required.'}, status=400)
            
            print(22)
            # check if account already exists
            accountNumber = data.get('accountNumber')
            account = Account.objects.filter(number=accountNumber).first()
            if account:
                return JsonResponse({'status': 'success', 'message': f'An account already exists with this {accountNumber}'})
            
            print(3)

            #Check for customer
            customerUid = data.get('customerUid')
            customer = Customer.objects.filter(uid=customerUid).first()
            if not customer:
                return JsonResponse({'status': 'error', 'message': f'There is no customer with UID: {customerUid}'}, status=400)
            
            print(4)

            #check for product
            product = None
            selectedModel = data.get('selectedModel')
            productModel = Model.objects.filter(name=selectedModel).first()
            if productModel:
                product = productModel.product
            if not productModel or not product:
                return JsonResponse({'status': 'error', 'message': f'There is no product with the selected model.'}, status=400)
            
            print(5)

            # Check for guarantors
            first_guarantor_uid = data.get('firstGuarantorUid')
            second_guarantor_uid = data.get('secondGuarantorUid')

            print(6)
            firstGuarantor = Guarantor.objects.filter(uid=first_guarantor_uid).first()
            secondGuarantor = Guarantor.objects.filter(uid=second_guarantor_uid).first()
            print(66)
            if not firstGuarantor or not secondGuarantor:
                return JsonResponse({'status': 'error', 'message': f'There is no guarantor with UID: {firstGuarantor} or UID: {second_guarantor_uid}'}, status=400)
            
            print(666)

            account = Account.objects.create(
                creator=user,
                number=accountNumber,
                saleDate=data.get('saleDate'),
                customer=customer, product=product
            )
            print(7)
            account.guarantors.add(firstGuarantor)
            account.guarantors.add(secondGuarantor)

            # contract = Contract.objects.create(
            #     cashValue=data['cashValue'], hireValue=data['hireValue'],
            #     downPayment=data['downPayment'], monthlyPayment=data['monthlyPayment'], length=data['length']
            # )
            # account.contract = contract
            account.save()
            print(8)
            
            return JsonResponse({
                'status': 'success', 'message': 'Account created successfully!',
                'data': {
                    'accountNumber': account.number,
                }
            })
        except Exception as e:
            print(e)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
