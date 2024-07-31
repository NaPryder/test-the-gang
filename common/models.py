from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):

    class Role(models.TextChoices):
        CUSTOMER = "CUSTOMER", _("CUSTOMER")
        ADMIN = "ADMIN", _("ADMIN")
        STAFF = "STAFF", _("STAFF")

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(choices=Role, default=Role.CUSTOMER)

    @classmethod
    def has_admin_role(cls, user):
        user_profile = cls.objects.filter(user=user).last()
        return user_profile and user_profile.role == cls.Role.ADMIN

    @classmethod
    def has_staff_role(cls, user):
        user_profile = cls.objects.filter(user=user).last()
        return user_profile and user_profile.role == cls.Role.STAFF

    @classmethod
    def has_customer_role(cls, user):
        user_profile = cls.objects.filter(user=user).last()
        return user_profile and user_profile.role == cls.Role.CUSTOMER
