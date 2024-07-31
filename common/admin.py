from django.contrib import admin
from common.models import Profile


admin.site.register(Profile, list_display=["id", "role", "user"])
