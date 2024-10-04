from django.core.management.base import BaseCommand
from bank.models import Transaction

class Command(BaseCommand):
    help = 'List all transactions'

    def handle(self, *args, **kwargs):
        transactions = Transaction.objects.all()
        for t in transactions:
            self.stdout.write(f"Account: {t.account.account_number}, Type: {t.transaction_type}, Amount: {t.amount}")
