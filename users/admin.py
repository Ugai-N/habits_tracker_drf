from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'first_name', 'email', 'is_superuser', 'is_staff', 'telegram', 'last_login')
    list_filter = ('is_superuser', 'is_staff', 'is_active',)
