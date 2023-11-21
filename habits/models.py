from django.db import models

from config import settings
from users.models import NULLABLE


class Frequency(models.IntegerChoices):
    DAYS = 0, 'дней'
    HOURS = 1, 'часов'
    MINUTES = 2, 'минут'
    SECONDS = 3, 'секунд'


class Habit(models.Model):
    is_pleasant = models.BooleanField(verbose_name='Приятная привычка?', default=False)
    is_public = models.BooleanField(verbose_name='Для общего доступа?', default=False)
    place = models.CharField(max_length=250, verbose_name='Место')
    action = models.CharField(max_length=1000, verbose_name='Действие')
    lead_time = models.PositiveSmallIntegerField(verbose_name='Кол-во секунд, необходимое для выполнения привычки')
    reward = models.TextField(verbose_name='Вознаграждение', **NULLABLE)
    relating_pleasant_habit = models.ForeignKey('self', on_delete=models.CASCADE,
                                                verbose_name='Связанная приятная привычка',
                                                related_name='related_habits', **NULLABLE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец",
                              related_name='habits')
    qty_per_period = models.PositiveSmallIntegerField(verbose_name='Каждые (указать кол-во интервалов)', default=1)
    period = models.CharField(max_length=150, choices=Frequency.choices, verbose_name='Интервал',
                              default=Frequency.DAYS)
    start_time = models.DateTimeField(verbose_name='Дата и время первого выполнения привычки')
