from django.forms import ValidationError
from rest_framework import serializers

from account.models import Account, Branch, Transaction


class AccountTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        read_only_fields = fields = [
            "transaction_type",
            "amount",
            "message",
            "transfer_to",
            "create_at",
        ]


class CustomerAccountDetailSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(decimal_places=2, max_digits=20, read_only=True)

    class Meta:
        model = Account
        read_only_fields = fields = [
            "account_type",
            "account_number",
            "branch",
            "status",
            "balance",
        ]


class BranchSerializer(serializers.PrimaryKeyRelatedField, serializers.ModelSerializer):
    branch_id = serializers.CharField(read_only=True)
    branch_name = serializers.CharField(read_only=True)

    class Meta:
        model = Branch
        fields = ["id", "branch_id", "branch_name"]


class CustomerCreateAccountSerializer(serializers.Serializer):

    username = serializers.CharField(required=True)
    balance = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
        coerce_to_string=False,
    )
    account_type = serializers.ChoiceField(choices=Account.Type.choices)
    branch_id = serializers.CharField(required=True)

    def validate_balance(self, value):
        if value <= 0:
            raise ValidationError("balance must be greater than 0")
        return value

    def validate_branch_id(self, value):
        if not value:
            raise ValidationError("require branch_id")

        return value

    def validate(self, attrs):
        branch_id = attrs["branch_id"]
        try:
            branch = Branch.objects.get(id=branch_id)
            attrs["branch"] = branch

        except:
            raise ValidationError(f"not found branch_id = {branch_id}")
        return attrs


class TransactionMakerSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=8, decimal_places=2, coerce_to_string=False
    )
    receiver_account_number = serializers.CharField(allow_blank=True, allow_null=True)

    def validate_amount(self, value):
        if value <= 0:
            raise ValidationError("balance must be greater than 0")
        return value
