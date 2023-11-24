from rest_framework.pagination import PageNumberPagination


class MyHabitsPaginator(PageNumberPagination):
    page_size = 2
