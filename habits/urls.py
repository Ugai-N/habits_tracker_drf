from django.urls import path

from habits.apps import HabitsConfig
from habits.views import HabitCreateAPIView, HabitListAPIView, HabitUpdateAPIView, HabitRetrieveAPIView, \
    HabitDeleteAPIView, PublicHabitListAPIView

app_name = HabitsConfig.name

urlpatterns = [
    path('create/', HabitCreateAPIView.as_view(), name='create_habit'),
    path('list_public', PublicHabitListAPIView.as_view(), name='list_public'),
    path('list', HabitListAPIView.as_view(), name='list_mine'),
    path('view/<int:pk>', HabitRetrieveAPIView.as_view(), name='view'),
    path('edit/<int:pk>', HabitUpdateAPIView.as_view(), name='edit'),
    path('delete/<int:pk>', HabitDeleteAPIView.as_view(), name='delete'),
]
