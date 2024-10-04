from django.contrib import admin

# Register your models here.
from .models import Transaction  # Adjust the import path if needed

# Register your model here
admin.site.register(Transaction)