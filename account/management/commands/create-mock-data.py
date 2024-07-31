from django.core.management import BaseCommand
from account.models import Branch, Account
from common.helpers import create_user
from common.models import Profile
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Start CLI"

    def handle(self, *args, **options):
        branch, _ = Branch.objects.get_or_create(
            branch_id="00000",
            branch_name="สำนักงานใหญ่",
        )
        branch.save()

        user_admin = create_user(
            username="test-admin", password="11test2@Pass04", role=Profile.Role.ADMIN
        )
        user_staff = create_user(
            username="test-staff", password="11test2@Pass04", role=Profile.Role.STAFF
        )

        user_a = create_user(
            username="test1", password="11test2@Pass04", role=Profile.Role.CUSTOMER
        )

        account_a = Account.objects.filter(account_number="0000000001").last()
        if not account_a:
            account_a = Account(
                account_number="0000000001",
                owner=user_a,
                balance=500,
                branch=branch,
            )
            account_a.save()
