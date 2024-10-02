from django.db import models
from django.contrib.auth.models import User

class Account(models.Model):

    ACCOUNT_TYPE_CHOICES = [
        ('checking', 'Checking Account'),
        ('savings', 'Savings Account'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    account_number = models.CharField(max_length=20, unique=True, default='0000000000')  # Default value added here

    def __str__(self):
        return f"{self.user.username} - {self.account_type} Account: {self.account_number} - Balance: {self.balance}"

class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=[('debit', 'Debit'), ('credit', 'Credit')])
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} of {self.amount}"


class Payee(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)

    def __str__(self):
        return f"Payee: {self.name}"

class BillPayment(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    payee = models.ForeignKey(Payee, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bill Payment of {self.amount} to {self.payee.name} on {self.date.strftime('%Y-%m-%d')}"
