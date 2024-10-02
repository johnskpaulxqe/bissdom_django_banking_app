from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from .models import Account, Transaction, Payee, BillPayment
from django.contrib.auth import logout as auth_logout
from .forms import RegisterForm
import random
import string

def home(request):
    return render(request, 'bank/home.html')

# Account Balance View
@login_required
def account_balance(request):
    # Get all accounts for the logged-in user
    accounts = Account.objects.filter(user=request.user)
    
    # Retrieve transactions for each account
    transactions = {account: Transaction.objects.filter(account=account).order_by('-timestamp') for account in accounts}

    return render(request, 'bank/account_balance.html', {'accounts': accounts, 'transactions': transactions})

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
    # Retrieve all accounts for the logged-in user
    accounts = Account.objects.filter(user=request.user)

    # Handle the case where no accounts exist
    if not accounts.exists():
        account = None
    else:
        account = accounts.first()  # You could also choose to leave this as None

    # Logic to process payees and bill payments
    if request.method == 'POST':
        payee_id = request.POST.get('payee_id')
        account_id = request.POST.get('account_id')  # Get selected account ID
        amount = request.POST.get('amount')

        try:
            payee = Payee.objects.get(id=payee_id)
            account = Account.objects.get(id=account_id)  # Retrieve the selected account
            BillPayment.objects.create(account=account, payee=payee, amount=amount)
            return redirect('bill_payment_success')
        except Payee.DoesNotExist:
            return render(request, 'bank/pay_bill.html', {'error': 'Payee does not exist.', 'accounts': accounts, 'payees': Payee.objects.all()})

    # Assuming you have Payees stored in the database
    payees = Payee.objects.all()
    return render(request, 'bank/pay_bill.html', {'account': account, 'payees': payees, 'accounts': accounts})


# User Registration View
def generate_account_number():
    return ''.join(random.choices(string.digits, k=10))  # Generates a random 10-digit account number

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create checking account
            checking_account = Account.objects.create(
                user=user,
                account_type='checking',
                balance=4500.00,
                account_number=generate_account_number()
            )
            # Create savings account
            savings_account = Account.objects.create(
                user=user,
                account_type='savings',
                balance=500.00,
                account_number=generate_account_number()
            )
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