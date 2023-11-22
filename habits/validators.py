from rest_framework import serializers

from habits.models import Habit


class HabitValidator:
    """Набор валидаторов для проверки полей при создании привычек"""
    # дока https://www.django-rest-framework.org/api-guide/validators/
    requires_context = True

    def __init__(self, field):
        self.field = field

    def __call__(self, value, serializer):
        field_value = dict(value).get(self.field)

        # если это полезная привычка, то проверяем чтобы было заполнено лишь одно поле:
        # либо reward, либо relating_pleasant_habit
        if not field_value:
            if (not serializer.initial_data['reward'] and not serializer.initial_data['relating_pleasant_habit']) or \
                    (serializer.initial_data['reward'] and serializer.initial_data['relating_pleasant_habit']):
                raise serializers.ValidationError(
                    "Необходимо заполнить ОДНО из полей: reward ИЛИ relating_pleasant_habit")
            # В связанные привычки могут попадать только привычки с признаком приятной привычки
            else:
                if serializer.initial_data['relating_pleasant_habit']:
                    if not Habit.objects.get(pk=serializer.initial_data['relating_pleasant_habit']).is_pleasant:
                        raise serializers.ValidationError("Связанной привычкой может быть только приятная привычка")
        # У приятной привычки не может быть вознаграждения или связанной привычки
        else:
            if serializer.initial_data['reward'] or serializer.initial_data['relating_pleasant_habit']:
                raise serializers.ValidationError(
                    "У полезной привычки не может быть вознаграждения или связанной приятной привычки")

        # Время выполнения должно быть не больше 120 секунд:
        if serializer.initial_data['lead_time'] > 120:
            raise serializers.ValidationError(
                "На выполнение привычки должно уходить не больше 120 секунд. Маленькими шагами к большой цели!")

        if serializer.initial_data['period'] == 0 and serializer.initial_data['qty_per_period'] > 7:
            raise serializers.ValidationError(
                "Чтобы привычка стала привычкой, ее нужно выполнять не реже, чем каждые 7 дней")
