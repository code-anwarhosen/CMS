from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Account

def HomeView(request):
    return render(request, 'pages/home.html')

def AccountView(request):

    if request.method == 'GET':
        accounts = Account.objects.all()
        serialized_data = [{
            'pk': acc.pk,
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

def AccountDetailsView(request, pk):
    account = Account.objects.filter(pk=pk).first()

    if not account:
        messages.info(request, 'This account does not exists!')
        return redirect('/')

    return render(request, 'pages/accountDetails.html', {'account': account})