from django.db import models
from django.contrib.auth.models import User

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)

    def __str__(self):
        return f"{self.user.username} - Balance: {self.balance}'s Account"

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
