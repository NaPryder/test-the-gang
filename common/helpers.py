from django.contrib.auth.models import User
from common.models import Profile


def create_user(username: str, password: str, role: Profile.Role, **kwargs):
    user = User.objects.filter(username=username).last()
    if not user:
        user = User(username=username, **kwargs)
        user.set_password(password)
        user.save()

    Profile.objects.get_or_create(role=role, user=user)

    return user
