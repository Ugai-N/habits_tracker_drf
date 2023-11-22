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

    ### перенесено в validators.py
    # def validate(self, data):
    #     """ """
    #     # если это полезная привычка, то проверяем чтобы было заполнено лишь одно поле:
    #     # либо reward, либо relating_pleasant_habit
    #     if not data['is_pleasant']:
    #         if (not data['reward'] and not data['relating_pleasant_habit']) or \
    #                 (data['reward'] and data['relating_pleasant_habit']):
    #             raise serializers.ValidationError(
    #                 "Необходимо заполнить ОДНО из полей: reward ИЛИ relating_pleasant_habit")
    #         # если заполнено relating_pleasant_habit, то оно должно быть связано с притяной привычкой
    #         else:
    #             if data['relating_pleasant_habit'] and not data['relating_pleasant_habit'].is_pleasant:
    #                 raise serializers.ValidationError("Связанной привычкой может быть только приятная привычка")
    #
    #     # если это приятная привычка, то проверяем чтобы поля reward и relating_pleasant_habit были пустыми
    #     else:
    #         if data['reward'] or data['relating_pleasant_habit']:
    #             raise serializers.ValidationError(
    #                 "У полезной привычки не может быть вознаграждения или связанной приятной привычки")
    #     return data

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
