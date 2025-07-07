from django.contrib.auth import get_user_model
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin

from users.serializers import UserCreateSerializer

User = get_user_model()


class UserCreateView(CreateModelMixin, GenericAPIView):
    """API endpoint for creating a new user"""

    queryset = User.objects.none()
    serializer_class = UserCreateSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
