from django_seed import Seed
from bank.models import Account, Transaction
import random

seeder = Seed.seeder()

# List of transaction types
transaction_types = ['debit', 'credit']

# Add transaction seeding logic
seeder.add_entity(Transaction, 100, {
    'account': lambda x: Account.objects.order_by('?').first(),  # Select random account
    'transaction_type': lambda x: random.choice(transaction_types),
    'amount': lambda x: round(random.uniform(10.00, 500.00), 2),
})

# Execute the seeding
inserted_pks = seeder.execute()

# Update the balances based on the transactions
for pk in inserted_pks[Transaction]:
    transaction = Transaction.objects.get(pk=pk)
    transaction.update_balance()
