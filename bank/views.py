from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from .models import Account, Transaction, Payee, BillPayment
from django.contrib.auth import logout as auth_logout
from .forms import RegisterForm

def home(request):
    return render(request, 'bank/home.html')

# Account Balance View
@login_required
def account_balance(request):
    # Attempt to retrieve the account and transactions for the logged-in user
    account = Account.objects.filter(user=request.user).first()
    
    if account:
        transactions = Transaction.objects.filter(account=account).order_by('-timestamp')  # Order transactions by date, most recent first
    else:
        transactions = []  # No transactions if the account does not exist

    return render(request, 'bank/account_balance.html', {'account': account, 'transactions': transactions})

# Transfer Money (Internal and External)
@login_required
def transfer_money(request):
    if request.method == 'POST':
        from_account = Account.objects.get(user=request.user)
        to_account = Account.objects.get(id=request.POST['to_account'])
        amount = request.POST['amount']
        # Deduct from sender's account
        Transaction.objects.create(account=from_account, amount=amount, transaction_type='debit')
        from_account.balance -= amount
        from_account.save()
        # Credit to receiver's account
        Transaction.objects.create(account=to_account, amount=amount, transaction_type='credit')
        to_account.balance += amount
        to_account.save()
        return redirect('account_balance')
    return render(request, 'bank/transfer_money.html')

# Add a Payee
@login_required
def add_payee(request):
    if request.method == 'POST':
        account = Account.objects.get(user=request.user)
        name = request.POST['name']
        account_number = request.POST['account_number']
        Payee.objects.create(account=account, name=name, account_number=account_number)
        return redirect('pay_bill')
    return render(request, 'bank/add_payee.html')

# Pay a Bill
@login_required
def pay_bill(request):
    try:
        account = Account.objects.get(user=request.user)
    except Account.DoesNotExist:
        # Handle the case where the account doesn't exist for the logged-in user
        account = None

    # Logic to process payees and bill payments
    if request.method == 'POST':
        payee_id = request.POST.get('payee_id')
        amount = request.POST.get('amount')
        try:
            payee = Payee.objects.get(id=payee_id)
            # Assuming you have a BillPayment model to handle the payment process
            BillPayment.objects.create(account=account, payee=payee, amount=amount)
            # Redirect to a success page or display a success message
            return redirect('bill_payment_success')
        except Payee.DoesNotExist:
            # Handle the case where the payee does not exist
            return render(request, 'bank/pay_bill.html', {'error': 'Payee does not exist.'})

    # Assuming you have Payees stored in the database
    payees = Payee.objects.all()
    return render(request, 'bank/pay_bill.html', {'account': account, 'payees': payees})

# User Registration View
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Account.objects.create(user=user, balance=500.00) 
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'bank/register.html', {'form': form})

# User Logout View
@login_required
def logout(request):
    auth_logout(request)
    return redirect('home')