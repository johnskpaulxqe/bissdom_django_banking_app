from django.db import migrations

def assign_default_account_type(apps, schema_editor):
    Account = apps.get_model('bank', 'Account')
    # Set default account_type for existing records
    Account.objects.filter(account_type__isnull=True).update(account_type='checking')  # Change as needed

class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0003_account_account_number_account_account_type_and_more'),  # Adjust if needed
    ]

    operations = [
        migrations.RunPython(assign_default_account_type),
    ]
