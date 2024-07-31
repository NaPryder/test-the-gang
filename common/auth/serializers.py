from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import django.contrib.auth.password_validation as validators
from rest_framework.validators import ValidationError
import re

from account.serializers import CustomerAccountDetailSerializer
from common.helpers import create_user
from common.models import Profile


class CustomerInquirySerializer(serializers.ModelSerializer):
    accounts = CustomerAccountDetailSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["username", "accounts"]
        read_only_fields = fields


class CustomerRegistrationSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        max_length=20, min_length=8, help_text="must be between 8 and 20 characters"
    )
    password = serializers.CharField(
        max_length=20,
        min_length=8,
        help_text="must be between 8 and 20 characters",
        write_only=True,
    )

    class Meta:
        model = User
        fields = ["username", "password"]

    def validate_username(self, username):
        pattern = r"^(?![-._])(?!.*[_.-]{2})[\w.-]{8,20}(?<![-._])$"
        if re.match(pattern, username) is None:
            raise ValidationError("Invalid username.")

        user = User.objects.filter(username=username).last()
        if user:
            raise ValidationError(f"Username has already used")

        return username

    def validate_password(self, password):
        validators.validate_password(password)
        return password

    def create(self, validated_data):
        password = validated_data.pop("password", None)

        user = create_user(
            username=validated_data["username"],
            password=password,
            role=Profile.Role.CUSTOMER,
        )
        return user


class SessionLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password"]

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")
        if username and password:
            user = authenticate(
                request=self.context.get("request"),
                username=username,
                password=password,
            )

            if not user:
                msg = "Unable to log in with provided credentials."
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user

        return attrs
