import json
from django_celery_beat.models import PeriodicTask, IntervalSchedule


def set_schedule(task_name, every, period, start_at, **kwargs):
    """Создаем расписание для таски"""
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=every,
        period=IntervalSchedule.PERIOD_CHOICES[period][0],
    )

    PeriodicTask.objects.create(
        interval=schedule,
        name=task_name,
        task='habits.tasks.send_telegram_message',
        kwargs=json.dumps({
            'telegram': kwargs['telegram'],
            'habit': kwargs['habit'],
            'reward': kwargs['reward'],
        }),
        start_time=start_at,
    )


def disable_task(obj):
    if PeriodicTask.objects.filter(name=f'id:{obj.pk}; {obj.action[:30]}').exists():
        needed_task = PeriodicTask.objects.get(name=f'id:{obj.pk}; {obj.action[:30]}')
        needed_task.enabled = False
        needed_task.save()
