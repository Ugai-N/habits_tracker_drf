import datetime

from django.urls import reverse
from django_celery_beat.models import PeriodicTask
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from habits.models import Habit
from users.models import User


class CreateTestCase(APITestCase):
    def setUp(self) -> None:
        # создаем и аутентифицируем пользователя
        self.client = APIClient()
        self.user = User.objects.create(email='777test@yandex.ru', password='SyncMaster11', telegram=6010128643)
        self.client.force_authenticate(user=self.user)

        # от имени аутентифицированного пользователя создаем полезную привычку
        self.habit = Habit.objects.create(
            is_pleasant=False,
            is_public=True,
            place='дома',
            action='пить стакан воды по утрам',
            lead_time=60,
            reward='массаж стоп',
            relating_pleasant_habit=None,
            owner=self.user,
            qty_per_period=1,
            period=0,
            start_time='2023-11-23T23:30:54+02:00'
        )

    def tearDown(self):
        # Очистит базу данных после теста и сбросьте счетчик id
        Habit.objects.all().delete()
        # self.instance.reset_sequences = True

    def test_setup(self):
        """Тестирование создание привычки в SetUp"""
        # self.instance.refresh_from_db()
        # print(f'test setup{Habit.objects.all()}')

        habit = Habit.objects.get(action='пить стакан воды по утрам')

        # проверяем что в базе появился новый урок
        self.assertEqual(habit.reward, 'массаж стоп')

        # проверяем что владелец присвоился
        self.assertEqual(habit.owner.email, '777test@yandex.ru')

        # проверяем что в базе всего 1 привычка
        self.assertEqual(
            Habit.objects.all().count(),
            1
        )

    def test_owner_create_pleasant(self):
        """Тестирование создания приятной привычки"""

        data = {
            'is_pleasant': True,
            'place': 'дома',
            'action': 'скушай яблочко',
            'lead_time': 90,
        }
        response = self.client.post(reverse('habits:create_habit'), data=data)

        # проверяем, что нет ошибок вывода страницы
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # проверяем, что owner - пользователь, установленный в сетапе
        self.assertEqual(Habit.objects.get(action='скушай яблочко').owner.email, '777test@yandex.ru')

    def test_create_habit(self):
        """Тестирование создания полезной привычки"""

        data = {
            'is_pleasant': False,
            'place': 'дома',
            'action': 'test',
            'lead_time': 60,
            'reward': 'массаж стоп',
            'start_time': '2023-11-24T17:08:11.457220+02:00'
        }
        response = self.client.post(reverse('habits:create_habit'), data=data)

        # проверяем, что нет ошибок вывода страницы
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # проверяем, структуру вывода
        self.assertEqual(response.json(),
                         {
                             'id': self.habit.id + 1,
                             'is_pleasant': False,
                             'is_public': False,
                             'place': 'дома',
                             'action': 'test',
                             'lead_time': 60,
                             'reward': 'массаж стоп',
                             'qty_per_period': 1,
                             'period': 0,
                             'start_time': '2023-11-24T17:08:11.457220+02:00',
                             'relating_pleasant_habit': None
                         }
                         )


class ValidationTestCase(APITestCase):
    def setUp(self) -> None:
        # создаем и аутентифицируем пользователя
        self.client = APIClient()
        self.user = User.objects.create(email='777test@yandex.ru', password='SyncMaster11', telegram=6010128643)
        self.client.force_authenticate(user=self.user)

        # от имени аутентифицированного пользователя создаем приятную привычку
        self.pleasant_habit = Habit.objects.create(
            is_pleasant=True,
            place='дома',
            action='массаж глаз',
            lead_time=60,
            owner=self.user
        )

        # от имени аутентифицированного пользователя создаем полезную привычку
        self.habit = Habit.objects.create(
            is_pleasant=False,
            place='дома',
            action='пить стакан воды по утрам',
            lead_time=60,
            reward='массаж стоп',
            owner=self.user
        )

        # создаем второго пользователя
        self.another_user = User.objects.create(email='another_user@yandex.ru', password='SyncMaster11', telegram=123)

        # от имени второго пользователя создаем приятную привычку
        self.another_user_pleasant_habit = Habit.objects.create(
            is_pleasant=True,
            place='в офисе',
            action='оставлять приятную записку себе на утро',
            lead_time=60,
            owner=self.another_user
        )

    def tearDown(self):
        # Очистит базу данных после теста и сбросьте счетчик id
        Habit.objects.all().delete()

    def test_reward_empty(self):
        """Тестирование создания полезной привычки при пустых полях reward и relating_pleasant_habit"""

        data = {
            'is_pleasant': False,
            'place': 'дома',
            'action': 'стоять в планке',
            'lead_time': 90,
        }
        response = self.client.post(reverse('habits:create_habit'), data=data)

        # проверяем, что есть ошибка вывода страницы
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # проверяем что выдается сообщение ктр мы записали
        self.assertEqual(
            response.json(),
            {'non_field_errors': ['Необходимо заполнить ОДНО из полей: reward ИЛИ relating_pleasant_habit']}
        )

    def test_two_rewards(self):
        """Тестирование создания полезной привычки при обоих заполненных полях reward и relating_pleasant_habit"""

        data = {
            'is_pleasant': False,
            'place': 'дома',
            'action': 'стоять в планке',
            'lead_time': 90,
            'reward': "съешь конфетку",
            'relating_pleasant_habit': self.pleasant_habit.pk,
        }
        response = self.client.post(reverse('habits:create_habit'), data=data)

        # проверяем, что есть ошибка вывода страницы
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # проверяем что выдается сообщение ктр мы записали
        self.assertEqual(
            response.json(),
            {'non_field_errors': ['Необходимо заполнить ОДНО из полей: reward ИЛИ relating_pleasant_habit']}
        )

    def test_relating_habit_not_pleasant(self):
        """Тестирование указания обычной привычки в качестве связанной приятной привычки"""

        data = {
            'is_pleasant': False,
            'place': 'дома',
            'action': 'стоять в планке',
            'lead_time': 90,
            'relating_pleasant_habit': self.habit.pk,
        }
        response = self.client.post(reverse('habits:create_habit'), data=data)

        # проверяем, что есть ошибка вывода страницы
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # проверяем что выдается сообщение ктр мы записали
        self.assertEqual(
            response.json(),
            {'non_field_errors': ['Связанной привычкой может быть только приятная привычка']}
        )

    def test_relating_habit_not_owner(self):
        """Тестирование указания приятной привычки другого пользователя в качестве связанной приятной привычки"""

        data = {
            'is_pleasant': False,
            'place': 'дома',
            'action': 'стоять в планке',
            'lead_time': 90,
            'relating_pleasant_habit': self.another_user_pleasant_habit.pk,
        }
        response = self.client.post(reverse('habits:create_habit'), data=data)

        # проверяем, что есть ошибка вывода страницы
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # проверяем что выдается сообщение ктр мы записали
        self.assertEqual(
            response.json(),
            {'non_field_errors': ['В качестве вознаграждения вы можете выбирать только свои приятные привычки']}
        )

    def test_pleasant_habit_has_reward(self):
        """Тестирование создяния приятной привычки с вознаграждением"""

        data = {
            'is_pleasant': True,
            'place': 'у зеркала',
            'action': 'улыбаться себе',
            'lead_time': 60,
            'relating_pleasant_habit': self.pleasant_habit.pk,
        }
        response = self.client.post(reverse('habits:create_habit'), data=data)

        # проверяем, что есть ошибка вывода страницы
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # проверяем что выдается сообщение ктр мы записали
        self.assertEqual(
            response.json(),
            {'non_field_errors': ['У приятной привычки не может быть вознаграждения или связанной приятной привычки']}
        )

    def test_lead_time(self):
        """Тестирование валидации поля lead_time"""

        data = {
            'is_pleasant': True,
            'place': 'у зеркала',
            'action': 'улыбаться себе',
            'lead_time': 150,
        }
        response = self.client.post(reverse('habits:create_habit'), data=data)

        # проверяем, что есть ошибка вывода страницы
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # проверяем что выдается сообщение ктр мы записали
        self.assertEqual(
            response.json(),
            {'non_field_errors': [
                'На выполнение привычки должно уходить от 1 до 120 секунд. Маленькими шагами к большой цели!']}
        )

    def test_frequency_validation(self):
        """Тестирование периодичности выполнения привычки (не реже, чем раз в 7 дней)"""

        data = {
            'is_pleasant': False,
            'place': 'на улице',
            'action': 'приседать',
            'reward': 'сходи в кино',
            'lead_time': 120,
            'qty_per_period': 10
        }
        response = self.client.post(reverse('habits:create_habit'), data=data)

        # проверяем, что есть ошибка вывода страницы
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # проверяем что выдается сообщение ктр мы записали
        self.assertEqual(
            response.json(),
            {'non_field_errors': ['Чтобы привычка стала привычкой, ее нужно выполнять не реже, чем каждые 7 дней']}
        )


class AccessTestCase(APITestCase):
    def setUp(self) -> None:
        # создаем и аутентифицируем пользователя
        self.client = APIClient()
        self.user = User.objects.create(email='777test@yandex.ru', password='SyncMaster11', telegram=6010128643)
        self.client.force_authenticate(user=self.user)

        # от имени аутентифицированного пользователя создаем полезную привычку
        self.habit = Habit.objects.create(
            is_pleasant=False,
            is_public=True,
            place='дома',
            action='пить стакан воды по утрам',
            lead_time=60,
            reward='массаж стоп',
            relating_pleasant_habit=None,
            owner=self.user,
            qty_per_period=1,
            period=0,
            start_time='2023-11-23T23:30:54+02:00'
        )
        # создаем второго пользователя
        self.another_user = User.objects.create(email='another_user@yandex.ru', password='SyncMaster11', telegram=123)

        # от имени второго пользователя создаем приятную привычку
        self.another_user_habit = Habit.objects.create(
            is_pleasant=False,
            is_public=True,
            place='в кровати',
            action='подводить итоги дня и хвалить себя',
            lead_time=120,
            owner=self.another_user
        )

    def tearDown(self):
        # Очистит базу данных после теста и сбросьте счетчик id
        Habit.objects.all().delete()
        # self.instance.reset_sequences = True

    def test_get_my_list(self):
        """Тестирование вывода списка привычек, где пользователь владелец"""

        my_list_response = self.client.get(reverse('habits:list_mine'))

        # проверяем что нет ошибок вывода страницы
        self.assertEqual(my_list_response.status_code, status.HTTP_200_OK)

        # проверяем, что пользователю выведется только 1 привычка, где он - владелец
        self.assertEqual(len(my_list_response.json()['results']), 1)

        # проверяем структуру вывода
        self.assertEqual(
            my_list_response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "id": self.habit.id,
                        "start_time": "2023-11-23T23:30:54+02:00",
                        "period_general": 'каждые 1 дней',
                        "description": 'Я буду пить стакан воды по утрам дома каждые 1 дней. '
                                       'Это занимает всего 60 секунд, а сколько гордости!',
                        "reward_general": 'массаж стоп',
                        "is_public": True,
                        "owner": self.user.id
                    },
                ]
            }
        )

    def test_get_public_list(self):
        """Тестирование вывода списка публичных привычек"""

        public_list_response = self.client.get(reverse('habits:list_public'))

        # проверяем что нет ошибок вывода страницы
        self.assertEqual(public_list_response.status_code, status.HTTP_200_OK)

        # проверяем, что пользователю выведется 2 привычки
        # (одна его, вторая - другого пользователя. Обе  установлены в Сетапе)
        self.assertEqual(len(public_list_response.json()), 2)

        # проверяем структуру вывода
        self.assertEqual(
            public_list_response.json()[1]['id'],
            self.another_user_habit.pk
        )

    def test_update(self):
        """Тестирование невозможности редактировать чужие привычки"""

        data = {
            'action': '_upd'
        }
        response = self.client.patch(f'/edit/{self.another_user_habit.pk}', data=data)

        # проверяем, что у пользователя нет прав
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete(self):
        """Тестирование невозможности удалять чужие привычки"""

        response = self.client.delete(f'/delete/{self.another_user_habit.pk}')

        # проверяем, что у пользователя нет прав
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TelegramTestCase(APITestCase):
    def setUp(self) -> None:
        # создаем и аутентифицируем пользователя
        self.client = APIClient()
        self.user = User.objects.create(email='777test@yandex.ru', password='SyncMaster11', telegram=6010128643)
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        # Очистит базу данных после теста и сбросьте счетчик id
        Habit.objects.all().delete()
        # self.instance.reset_sequences = True

    def test_scheduling_task_pleasant(self):
        """Тестирование планирования задачи по приятной привычки (задача не планируется)"""

        data = {
            'is_pleasant': True,
            'place': 'дома',
            'action': 'скушай яблочко',
            'lead_time': 90,
        }
        response = self.client.post(reverse('habits:create_habit'), data=data)

        # проверяем, что нет ошибок вывода страницы
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # проверяем, что запланировалась задача
        self.assertEqual(PeriodicTask.objects.all().count(), 0)

    def test_scheduling_task(self):
        """Тестирование планирования задачи по полезной привычке"""

        data = {
            'is_pleasant': False,
            'place': 'дома',
            'action': 'test',
            'lead_time': 60,
            'reward': 'массаж стоп',
            'start_time': '2023-11-24T19:23:54+02:00',
        }
        response = self.client.post(reverse('habits:create_habit'), data=data)

        # проверяем, что нет ошибок вывода страницы
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # проверяем, что запланировалась задача
        self.assertEqual(PeriodicTask.objects.all().count(), 1)

        # проверяем, что запланированная задача на созданную привычку
        self.assertEqual(PeriodicTask.objects.get(
            name=f'id:{response.json()["id"]}; {response.json()["action"][:30]}').start_time,
                         datetime.datetime(2023, 11, 24, 17, 23, 54, tzinfo=datetime.timezone.utc))

        # проверяем, что задача активна
        self.assertEqual(PeriodicTask.objects.all().first().enabled, True)

    def test_disabling_task(self):
        """Тестирование остановки задачи при удалении привычки"""

        data = {
            'is_pleasant': False,
            'place': 'дома',
            'action': 'test',
            'lead_time': 60,
            'reward': 'массаж стоп',
            'start_time': '2023-11-24T19:23:54+02:00',
        }
        response = self.client.post(reverse('habits:create_habit'), data=data)

        # проверяем, что задача активна
        self.assertEqual(PeriodicTask.objects.all().first().enabled, True)

        response = self.client.delete(f'/delete/{response.json()["id"]}')

        # проверяем, что задача не активна
        self.assertEqual(PeriodicTask.objects.all().first().enabled, False)
