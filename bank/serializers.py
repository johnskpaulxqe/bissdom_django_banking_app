from rest_framework import serializers

class AddFundsSerializer(serializers.Serializer):
    account_number = serializers.CharField(max_length=20)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
