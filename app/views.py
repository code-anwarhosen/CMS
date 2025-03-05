from django.shortcuts import render
from django.http import JsonResponse
from .models import Customer

def HomeView(request):
    return render(request, 'pages/home.html')

def CustomerView(request):
    if request.method == 'GET':
        customers = Customer.objects.all()
        serialized_data = [{
            'name': cus.name,
            'phone': cus.phone,
            'account': '',
            'due': 0,
            'avatar': cus.avatar.url,
            'status': 'active',
        } for cus in customers]
        return JsonResponse({'customers': customers})