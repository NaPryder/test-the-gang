from rest_framework import routers

from common.views import LoginViewSet, CustomerRegistrationViewSet

router = routers.DefaultRouter()
router.register("login", LoginViewSet, basename="login")
router.register("registration", CustomerRegistrationViewSet, basename="registration")

urlpatterns = router.urls
