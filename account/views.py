import datetime
from django.http import QueryDict
from rest_framework import mixins, viewsets
from django.shortcuts import render
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    DjangoObjectPermissions,
)
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action
from account.models import Account
from account.serializers import (
    AccountTransactionSerializer,
    CustomerAccountDetailSerializer,
    CustomerCreateAccountSerializer,
    TransactionMakerSerializer,
)
from django.contrib.auth.models import User

from common.auth.permissions import AdminOrStaffPermission, CustomerAccessPermission

from django.db import transaction

from common.auth.serializers import CustomerInquirySerializer
from utils.date_utils import now, parse_datetime
from dateutil.relativedelta import relativedelta


# Create your views here.
class CustomerAccountManageViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.select_related("owner", "branch").all()
    permission_classes = [IsAuthenticated, AdminOrStaffPermission]
    serializer_class = CustomerAccountDetailSerializer

    def list(self, request, *args, **kwargs):
        return Response(data=[])

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        account = self.get_queryset().filter(account_number=pk)
        data = CustomerAccountDetailSerializer(
            account, context={"request": request}
        ).data
        return Response(data)

    @action(
        methods=["POST"],
        detail=False,
        serializer_class=CustomerCreateAccountSerializer,
    )
    def create_account(self, request):
        data = request.data
        username = data.get("username")

        user = User.objects.filter(username=username).last()
        if not user:
            raise NotFound("Not found user")

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        branch = validated_data.get("branch")
        balance = validated_data.get("balance")
        account_type = validated_data.get("account_type")

        account = Account.create_account(
            maker=request.user,
            owner=user,
            balance=balance,
            branch=branch,
            account_type=account_type,
        )

        return Response(data=f"create account {account}", status=201)

    @action(methods=["PUT"], detail=True)
    def activate(self, request, pk):

        # select for update instance
        with transaction.atomic():
            account = (
                Account.objects.select_for_update().filter(account_number=pk).last()
            )
            if not account:
                raise NotFound("Invalid Account")

            if not account.activate(maker=request.user):
                raise NotFound("Already activated")

            return Response(f"Activated account {account}")

    @action(methods=["PUT"], detail=True)
    def deactivate(self, request, pk):

        # select for update instance
        with transaction.atomic():
            account = (
                Account.objects.select_for_update().filter(account_number=pk).last()
            )
            if not account:
                raise NotFound("Invalid Account")

            if not account.deactivate(maker=request.user):
                raise NotFound("Already deactivated")

            return Response(f"Deactivated account {account}")

    @action(
        methods=["PUT"],
        detail=True,
        serializer_class=TransactionMakerSerializer,
        permission_classes=[AdminOrStaffPermission],
    )
    def deposit(self, request, pk):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        amount = validated_data.get("amount")

        # select for update instance
        with transaction.atomic():
            account = (
                Account.objects.select_for_update().filter(account_number=pk).last()
            )
            if not account:
                raise NotFound("Invalid account")
            if account.status != Account.Status.ACTIVE:
                raise NotFound("Account is locked, Please contact admin for unlock.")

            # update
            account.deposit(amount=float(amount), maker=self.request.user)

            return Response(
                f"Deposit {amount} to account {account}. Balance = {account.balance}"
            )

    @action(
        methods=["PUT"],
        detail=True,
        serializer_class=TransactionMakerSerializer,
        permission_classes=[AdminOrStaffPermission],
    )
    def withdraw(self, request, pk):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        amount = validated_data.get("amount")

        # select for update instance
        with transaction.atomic():
            account = (
                Account.objects.select_for_update().filter(account_number=pk).last()
            )
            if not account:
                raise NotFound("Invalid account")
            if account.status != Account.Status.ACTIVE:
                raise NotFound("Account is locked, Please contact admin for unlock.")

            try:
                # update
                account.withdraw(amount=float(amount), maker=self.request.user)
            except Exception as error:
                raise NotFound(str(error))

            return Response(
                f"Withdraw {amount} to account {account}. Balance = {account.balance}"
            )

    @action(
        methods=["PUT"],
        detail=True,
        serializer_class=TransactionMakerSerializer,
        permission_classes=[AdminOrStaffPermission],
    )
    def transfer(self, request, pk):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        amount = validated_data.get("amount")
        receiver_account_number = validated_data.get("receiver_account_number")

        # select for update instance
        with transaction.atomic():

            receiver_account = (
                Account.objects.select_for_update()
                .filter(
                    account_number=receiver_account_number,
                    status=Account.Status.ACTIVE,
                )
                .last()
            )
            if not receiver_account:
                raise NotFound("Invalid receiver account")

            account = (
                Account.objects.select_for_update()
                .filter(
                    account_number=pk,
                    status=Account.Status.ACTIVE,
                )
                .last()
            )
            if not account:
                raise NotFound("Invalid account")
            if account.status != Account.Status.ACTIVE:
                raise NotFound("Account is locked, Please contact admin for unlock.")

            if receiver_account.account_number == account.account_number:
                raise NotFound("Cannot Process")

            try:
                # update
                account.transfer(
                    amount=float(amount),
                    receiver_account=receiver_account,
                    maker=self.request.user,
                )
            except Exception as error:
                raise NotFound(str(error))

            return Response(f"Transfer {amount} to account {receiver_account}.")


class CustomerInquiryViewSet(viewsets.ModelViewSet):
    queryset = (
        Account.objects.select_related("owner", "branch")
        .prefetch_related("transactions")
        .all()
    )
    permission_classes = [IsAuthenticated, CustomerAccessPermission]
    serializer_class = CustomerInquirySerializer
    lookup_field = "account_number"

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset.filter(owner=self.request.user)

    def list(self, request, *args, **kwargs):

        data = CustomerInquirySerializer(
            request.user, context={"request": request}
        ).data
        return Response(data)

    @action(methods=["GET"], detail=True, serializer_class=AccountTransactionSerializer)
    def statement(self, request, account_number):
        params: QueryDict = request.query_params

        start_date = parse_datetime(params.get("start_date"))
        end_date = parse_datetime(params.get("end_date"))
        filter_condition = {}

        if start_date is None:
            start_date = (now() - relativedelta(months=6)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        if end_date is None:
            end_date = now().replace(hour=0, minute=0, second=0, microsecond=0)

        elif isinstance(start_date, datetime.datetime):
            filter_condition["create_at__gte"] = start_date

        elif isinstance(end_date, datetime.datetime):
            filter_condition["create_at__lte"] = end_date

        if start_date > end_date:
            raise NotFound("Invalid start date and end date")

        account = self.get_queryset().filter(account_number=account_number).last()
        if not account:
            raise NotFound("Invalid account")
        transactions = account.transactions.filter(**filter_condition)
        serializer = self.get_serializer(
            transactions, context={"request": request}, many=True
        )

        return Response(data=serializer.data)
