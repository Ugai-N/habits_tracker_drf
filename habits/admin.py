from django.contrib import admin

from habits.models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    fields = ['owner', 'is_pleasant', 'action', 'lead_time', 'is_public', 'reward', 'relating_pleasant_habit',
              'start_time', 'qty_per_period', 'period']
    list_display = ('pk', 'owner', 'is_pleasant', 'action', 'lead_time', 'is_public', 'reward', 'relating_pleasant_habit',
                    'start_time', 'qty_per_period', 'period')
    list_filter = ('owner', 'is_pleasant', 'is_public', 'period')
    search_fields = ('action',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """переопределяем поле owner в форме -> устанавливаем значение по умолчанию + в режиме readonly"""
        if db_field.name == "owner":
            # setting the user from the request object
            kwargs["initial"] = request.user
            # making the field readonly
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
