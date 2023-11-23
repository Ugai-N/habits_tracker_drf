from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated

from habits.models import Habit
from habits.paginators import MyHabitsPaginator
from habits.permissions import IsModerator, IsOwner
from habits.serializers import HabitSerializer, CreateHabitSerializer


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

    # def perform_create(self, serializer):
    #     """Сохраняем текущего пользователя владельцем (owner)"""
    #     new_habit = serializer.save()
    #     new_habit.owner = self.request.user
    #     new_habit.save()
    #     # update_course_data.delay(new_lesson.pk, 'Lesson', 'Создан')


class HabitRetrieveAPIView(RetrieveAPIView):
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]


class HabitUpdateAPIView(UpdateAPIView):
    serializer_class = CreateHabitSerializer
    queryset = Habit.objects.all()
    permission_classes = [IsAuthenticated, IsOwner | IsModerator]

    # def perform_update(self, serializer):
    #     updated_lesson = serializer.save()
    #     update_course_data.delay(updated_lesson.pk, 'Lesson', 'Изменен')


class HabitDeleteAPIView(DestroyAPIView):
    queryset = Habit.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]
