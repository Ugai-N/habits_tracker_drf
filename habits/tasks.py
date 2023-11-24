import requests
from celery import shared_task
from django.conf import settings


@shared_task
def send_telegram_message(telegram, habit, reward):
    """Таска для отправки уведомления в телеграм"""
    requests.post(
        url=f'{settings.TELEGRAM_URL}{settings.TELEGRAM_TOKEN}/sendMessage',
        data={
            'chat_id': telegram,
            'text': f'Время сделать еще один шаг на пути к лучшей версии себя и выполнить привычку "{habit}". '
                    f'А хорошие девочки и мальчики за это получают вознаграждение. Так что и ты {reward}'
        }
    )
