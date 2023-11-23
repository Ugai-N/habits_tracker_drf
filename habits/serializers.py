from rest_framework import serializers

from habits.models import Habit
from habits.validators import HabitValidator


class PleasantHabitSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода связанной приятной привычки в списке полезных привычек"""
    description = serializers.SerializerMethodField()

    def get_description(self, instance):
        """Определяем описательную часть приятной привычки"""
        return f'Ты молодец! Поэтому {instance.action}. ' \
               f'Это занимает всего {instance.lead_time} секунд, а сколько радости!'

    class Meta:
        model = Habit
        fields = ('id', 'description', 'owner',)


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода списка полезных привычек"""
    description = serializers.SerializerMethodField()
    reward_general = serializers.SerializerMethodField()
    period_general = serializers.SerializerMethodField()

    def get_period_general(self, instance):
        return f'каждые {instance.qty_per_period} {instance.get_period_display()}'

    def get_reward_general(self, instance):
        if not instance.is_pleasant:
            if instance.reward:
                return instance.reward
            else:
                return PleasantHabitSerializer(instance.relating_pleasant_habit).data

    def get_description(self, instance):
        return f'Я буду {instance.action} {instance.place} каждые {instance.qty_per_period} ' \
               f'{instance.get_period_display()}. Это занимает всего {instance.lead_time} секунд, а сколько гордости!'

    class Meta:
        model = Habit
        fields = ('id', 'start_time', 'period_general', 'description', 'reward_general', 'is_public', 'owner')


class CreateHabitSerializer(serializers.ModelSerializer):
    """Сериализатор для создания привычки"""

    # встроенный способ записать текущего пользователя в поле Владельца
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Habit
        fields = '__all__'
        validators = [
            HabitValidator(field='is_pleasant'),
            serializers.UniqueTogetherValidator(fields=['action', 'owner'],
                                                queryset=Habit.objects.all(),
                                                )
        ]
        read_only_fields = ('owner',)
