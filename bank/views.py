from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from .models import Account, Transaction, Payee, BillPayment
from django.contrib.auth import logout as auth_logout
from .forms import RegisterForm
from django.db import models
from django.db.models import Sum, F, Case, When
import random
import string
from .models import Account  # Make sure to import your Account model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import AddFundsSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from django.utils import timezone
from django.contrib import messages


def home(request):
    return render(request, 'bank/home.html')

# Account Balance View
@login_required
def account_balance(request):
    # Get all accounts for the logged-in user
    accounts = Account.objects.filter(user=request.user).prefetch_related('transaction_set')

    # Iterate through the user's accounts to calculate balances
    for account in accounts:
        # If there are transactions, recalculate balance based on them
        if account.transaction_set.exists():
            # Aggregate balance from transactions
            balance = account.transaction_set.aggregate(
                total_deposit=Sum(Case(
                    When(transaction_type='deposit', then=F('amount')),
                    default=0,
                    output_field=models.DecimalField(),
                )),
                total_withdrawal=Sum(Case(
                    When(transaction_type='withdrawal', then=F('amount')),
                    default=0,
                    output_field=models.DecimalField(),
                )),
                total_bill_payment=Sum(Case(
                    When(transaction_type='bill_payment', then=F('amount')),
                    default=0,
                    output_field=models.DecimalField(),
                )),
                total_transfer=Sum(Case(
                    When(transaction_type='transfer', then=F('amount')),
                    default=0,
                    output_field=models.DecimalField(),
                )),
            )

            # Safeguard against None values by setting default values to 0
            total_deposit = balance['total_deposit'] if balance['total_deposit'] is not None else 0
            total_withdrawal = balance['total_withdrawal'] if balance['total_withdrawal'] is not None else 0
            total_bill_payment = balance['total_bill_payment'] if balance['total_bill_payment'] is not None else 0
            total_transfer = balance['total_transfer'] if balance['total_transfer'] is not None else 0

            # Recalculate balance based on transactions
            account.balance = total_deposit - (total_withdrawal + total_bill_payment + total_transfer)
        
        # Save updated balance to the account
        account.save()

    # Pass the accounts to the template
    return render(request, 'bank/account_balance.html', {'accounts': accounts})


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
    accounts = Account.objects.filter(user=request.user)  # Get all accounts for the user
    if request.method == 'POST':
        account = Account.objects.get(id=request.POST['account'])  # Get the selected account
        name = request.POST['name']
        account_number = request.POST['account_number']
        
        try:
            Payee.objects.create(account=account, name=name, account_number=account_number)
            messages.success(request, 'Payee added successfully!')
            return redirect('pay_bill')
        except Exception as e:
            messages.error(request, 'Failed to add payee: ' + str(e))
            return render(request, 'bank/add_payee.html', {'accounts': accounts})

    return render(request, 'bank/add_payee.html', {'accounts': accounts})

# Pay a Bill
@login_required
def pay_bill(request):
    # Get all accounts for the logged-in user (balance is assumed to be pre-calculated and stored)
    accounts = Account.objects.filter(user=request.user)

    if request.method == 'POST':
        payee_id = request.POST.get('payee_id')
        account_id = request.POST.get('account_id')
        amount = request.POST.get('amount')

        try:
            payee = Payee.objects.get(id=payee_id)
            account = Account.objects.get(id=account_id)

            # Validate amount
            if float(amount) <= 0:
                messages.error(request, 'Amount must be greater than zero.')
            else:
                # Create the bill payment
                BillPayment.objects.create(account=account, payee=payee, amount=amount)

                # Create a transaction for the bill payment (withdrawal)
                Transaction.objects.create(
                    account=account,
                    transaction_type='bill_payment',  # Assuming this is the type for payments
                    amount=amount,
                )

                messages.success(request, 'Bill payment successful!')

        except Payee.DoesNotExist:
            messages.error(request, 'Payee does not exist.')
        except Account.DoesNotExist:
            messages.error(request, 'Account does not exist.')

        # Redirect to the same page after processing the payment
        return redirect('pay_bill')  # Ensure you have 'pay_bill' in your URL configuration

    # Fetch payees stored in the database
    payees = Payee.objects.all()

    # Render the page with accounts and payees
    return render(request, 'bank/pay_bill.html', {
        'accounts': accounts,
        'payees': payees,
    })

# Bill Payment success message - not bein used 
@login_required
def bill_payment_success(request):
    return render(request, 'bank/bill_payment_success.html')

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

@login_required
def create_transaction(request, account_id):
    account = get_object_or_404(Account, id=account_id)

    if request.method == 'POST':
        amount = request.POST.get('amount')
        transaction_type = request.POST.get('transaction_type')

        transaction = Transaction(account=account, amount=amount, transaction_type=transaction_type)
        transaction.save()  # This will also update the balance

        return redirect('account_balance')

    return render(request, 'bank/create_transaction.html', {'account': account})


# User Logout View
@login_required
def logout(request):
    auth_logout(request)
    return redirect('home')


# Add Fund
class AddFundsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddFundsSerializer(data=request.data)
        if serializer.is_valid():
            account_number = serializer.validated_data['account_number']
            amount = serializer.validated_data['amount']

            # Get the account based on the account number
            try:
                account = Account.objects.get(account_number=account_number, user=request.user)
            except Account.DoesNotExist:
                return Response({'error': 'Account not found.'}, status=status.HTTP_404_NOT_FOUND)

            # Add the amount to the balance
            account.balance += amount
            account.save()

            # Create a new transaction and set the type as "deposit"
            transaction = Transaction.objects.create(
                account=account,
                amount=amount,
                transaction_type='deposit'
            )

            return Response({'message': 'Funds added successfully!', 'new_balance': account.balance, 'transaction_id': transaction.id}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   

#Obtaining API Token
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
