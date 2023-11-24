from rest_framework.generics import CreateAPIView

from users.serializers import UserRegisterSerializer


class UserCreateAPIView(CreateAPIView):
    """Представление для регистрации нового пользователя"""
    serializer_class = UserRegisterSerializer
