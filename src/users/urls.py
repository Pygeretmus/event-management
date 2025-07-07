from django.urls import path

from users.views import UserCreateView

urlpatterns = [
    path("create/", UserCreateView.as_view(), name="user-create"),
]
