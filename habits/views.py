from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated

from habits.models import Habit
from habits.paginators import MyHabitsPaginator
from habits.permissions import IsModerator, IsOwner
from habits.serializers import HabitSerializer, CreateHabitSerializer
from habits.services import set_schedule, disable_task


class HabitListAPIView(ListAPIView):
    """Представление для вывода списка полезных привычек, где владелец - текущий пользователь или модератор"""
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = MyHabitsPaginator

    def get_queryset(self, *args, **kwargs):
        """Выводим список полезных привычек, по которым пользователь является владельцем или модератором"""
        queryset = Habit.objects.filter(is_pleasant=False)
        if not self.request.user.groups.filter(name='Модератор').exists():
            queryset = queryset.filter(owner=self.request.user)
        return queryset.order_by('id')


class PublicHabitListAPIView(ListAPIView):
    """Представление для вывода списка полезных привычек, находящихся в общем доступе"""
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        """Выводим список опубликованных полезных привычек"""
        queryset = Habit.objects.filter(is_pleasant=False) & Habit.objects.filter(is_public=True)
        return queryset.order_by('id')


class HabitCreateAPIView(CreateAPIView):
    serializer_class = CreateHabitSerializer
    permission_classes = [IsAuthenticated, ~IsModerator]

    def perform_create(self, serializer):
        """При создании полезной привычки заводим расписание на отправку уведомлений
        о необходимости выполнить привычку"""
        new_habit = serializer.save()
        if not new_habit.is_pleasant:
            set_schedule(
                task_name=f'id:{new_habit.pk}; {new_habit.action[:30]}',
                every=new_habit.qty_per_period,
                period=new_habit.period,
                start_at=new_habit.start_time,
                telegram=new_habit.owner.telegram,
                habit=new_habit.action,
                reward=new_habit.reward if new_habit.reward else new_habit.relating_pleasant_habit.action
            )


class HabitRetrieveAPIView(RetrieveAPIView):
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]


class HabitUpdateAPIView(UpdateAPIView):
    serializer_class = CreateHabitSerializer
    queryset = Habit.objects.all()
    permission_classes = [IsAuthenticated, IsOwner | IsModerator]


class HabitDeleteAPIView(DestroyAPIView):
    queryset = Habit.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]

    def delete(self, request, *args, **kwargs):
        disable_task(self.get_object())
        return self.destroy(request, *args, **kwargs)
