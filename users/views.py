from rest_framework.generics import CreateAPIView

from users.serializers import UserRegisterSerializer


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserRegisterSerializer
