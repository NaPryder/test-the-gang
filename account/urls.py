from rest_framework import routers
from account.views import CustomerAccountManageViewSet, CustomerInquiryViewSet

router = routers.DefaultRouter()
router.register("customer", CustomerAccountManageViewSet, basename="customer")
router.register("financial", CustomerInquiryViewSet, basename="financial")

urlpatterns = router.urls
