from django.contrib import admin
from account.models import Branch, Account, AccountLog, Transaction

# Register your models here.
admin.site.register(
    Branch, list_display=["id", "branch_id", "branch_name", "is_active"]
)
admin.site.register(
    Account,
    list_display=[
        "id",
        "account_type",
        "branch",
        "status",
        "account_number",
        "owner",
        "balance",
        "create_at",
    ],
)
admin.site.register(
    AccountLog,
    list_display=["id", "message", "create_at"],
)
admin.site.register(
    Transaction,
    list_display=[
        "id",
        "account",
        "transaction_type",
        "message",
        "maker",
        "create_at",
    ],
)
