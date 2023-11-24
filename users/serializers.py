from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Cериалайзер для User"""
    class Meta:
        model = User
        fields = '__all__'


class UserRegisterSerializer(serializers.ModelSerializer):
    """Cериалайзер для регистрации User"""

    # widget = Entry('password', show="*", width=15)
    # password2 = getpass.getpass()

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'telegram', 'password', 'password2')

    def validate(self, attrs):
        """Проверка на совпадение паролей"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают!"})
        return attrs

    def create(self, validated_data):
        """Переопределяем метод create для создания пользователя:
        создаем в БД пользователя с указанным адресом эл.почты и телеграммом, хешируем пароль"""

        user = User.objects.create(
            email=validated_data['email'],
            telegram=validated_data['telegram']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
