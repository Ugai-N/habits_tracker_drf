import os

from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.create(
            email='admin@habits.ru',
            first_name='NN',
            last_name='UU',
            is_staff=True,
            is_superuser=True,
            telegram='123456789',
        )
        user.set_password('123')
        user.save()
