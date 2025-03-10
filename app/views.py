from django.shortcuts import render
from django.http import JsonResponse
from .models import Account

def HomeView(request):
    return render(request, 'pages/home.html')

def AccountView(request):

    if request.method == 'GET':
        accounts = Account.objects.all()
        serialized_data = [{
            'name': acc.customer.name if acc.customer else "Unknown",
            'phone': acc.customer.phone if acc.customer else "N/A",
            'account': acc.number,
            'balance': 100,
            'avatar': acc.customer.avatar.url if acc.customer and acc.customer.avatar else None,
            'status': acc.status,
        } for acc in accounts]
        return JsonResponse({'accounts': serialized_data})
    
    elif request.method == 'POST':
        pass