from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from common.auth.permissions import AdminOrStaffPermission
from rest_framework import viewsets, serializers, mixins
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    DjangoObjectPermissions,
)
from common.auth.serializers import (
    CustomerInquirySerializer,
    CustomerRegistrationSerializer,
    SessionLoginSerializer,
)
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.middleware.csrf import get_token

from common.models import Profile


# Create your views here.
class LoginViewSet(viewsets.GenericViewSet):
    serializer_class = SessionLoginSerializer
    permission_classes = [AllowAny]

    @method_decorator(never_cache)
    @method_decorator(csrf_protect)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data["user"]
        except Exception as e:
            return Response("Unable to log in with provided credentials.", 400)

        login(request, user)

        if Profile.has_admin_role(user) or Profile.has_staff_role(user):
            data = f"Welcome {user}"
        else:
            data = CustomerInquirySerializer(user, context={"request": request}).data
        response = Response(data=data)
        response.set_cookie("token", get_token(request))
        return response

    def get_view_name(self):
        return "Login"


class CustomerRegistrationViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, AdminOrStaffPermission]
    serializer_class = CustomerRegistrationSerializer
