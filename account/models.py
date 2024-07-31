from typing import Iterable
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class Branch(models.Model):

    branch_id = models.CharField(max_length=5, unique=True)
    branch_name = models.CharField()
    is_active = models.BooleanField(default=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.branch_name} ({self.branch_id})"


class Account(models.Model):

    class Type(models.TextChoices):
        SAVING = "01", _("SAVING")
        FIXED = "02", _("FIXED DEPOSIT")

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", _("ACTIVE")
        INACTIVE = "INACTIVE", _("INACTIVE")
        WAIT_ACTIVATE = "WAIT", _("WAIT ACTIVATE")

    account_type = models.CharField(choices=Type, default=Type.SAVING)
    status = models.CharField(choices=Status, default=Status.WAIT_ACTIVATE)
    account_number = models.CharField(max_length=16, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accounts")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="branch")
    balance = models.DecimalField(max_digits=21, decimal_places=2)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Account ({self.account_number})"

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE

    def set_log(self, message: str):
        AccountLog.objects.create(account=self, message=message)

    @classmethod
    def create_account(
        cls,
        maker: User,
        owner: User,
        balance: float,
        branch: Branch,
        account_type: Type,
    ):
        from common.models import Profile

        if Profile.has_admin_role(maker) or Profile.has_staff_role(maker):

            # generate account number
            last_account_number = cls.objects.filter(branch=branch).count() + 1

            account_number = (
                branch.branch_id + account_type + str(last_account_number).zfill(9)
            )

            account = cls.objects.create(
                account_number=account_number,
                owner=owner,
                balance=balance,
                branch=branch,
                account_type=account_type,
            )

            account.set_log(f"create account by {maker}")

            return account

    def activate(self, maker: User):
        from common.models import Profile

        if self.status == self.Status.ACTIVE:
            return None

        elif Profile.has_admin_role(maker) or Profile.has_staff_role(maker):
            self.status = self.Status.ACTIVE
            self.set_log(f"activate account by {maker}")
            self.save()
            return True

        return None

    def deactivate(self, maker: User):
        from common.models import Profile

        if self.status != self.Status.ACTIVE:
            return None
        elif self.status == self.Status.WAIT_ACTIVATE:
            return None

        elif Profile.has_admin_role(maker) or Profile.has_staff_role(maker):
            self.status = self.Status.INACTIVE
            self.set_log(f"deactivate account by {maker}")
            self.save()
            return True

        return None

    def deposit(self, amount: float, maker: User, set_log: bool = True):
        self.balance = float(self.balance) + amount

        self.save()
        if set_log:
            Transaction.objects.create(
                account=self,
                transaction_type=Transaction.Type.DEPOSIT,
                amount=amount,
                message="Complete Deposit",
                maker=maker,
            )

    def withdraw(self, amount: float, maker: User, set_log: bool = True):

        if amount < 0:
            raise Exception("Invalid amount")

        new_balance = float(self.balance) - amount
        if new_balance < 0:
            raise Exception("Cannot withdraw")

        self.balance = new_balance

        self.save()
        if set_log:
            Transaction.objects.create(
                account=self,
                transaction_type=Transaction.Type.WITHDRAW,
                amount=amount,
                message="Complete Withdraw",
                maker=maker,
            )

    def transfer(self, amount: float, receiver_account: "Account", maker: User):

        self.withdraw(amount, maker, set_log=False)
        Transaction.objects.create(
            account=self,
            transaction_type=Transaction.Type.TRANSFER,
            amount=amount,
            message="Complete Transfer",
            transfer_to=receiver_account,
            maker=maker,
        )

        receiver_account.deposit(amount, maker)


class AccountLog(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="log")
    message = models.CharField(null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)


class Transaction(models.Model):

    class Type(models.TextChoices):
        DEPOSIT = "D", _("DEPOSIT")
        WITHDRAW = "W", _("WITHDRAW")
        TRANSFER = "T", _("TRANSFER")

    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="transactions"
    )
    transaction_type = models.CharField(choices=Type)
    amount = models.DecimalField(max_digits=21, decimal_places=2)
    message = models.CharField(null=True, blank=True)
    transfer_to = models.ForeignKey(
        Account, on_delete=models.PROTECT, null=True, blank=True
    )

    maker = models.ForeignKey(User, on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)
