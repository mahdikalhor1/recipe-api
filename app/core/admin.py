from django.contrib import admin
from . import models
from django.contrib.auth.admin import UserAdmin

class UserModelAdmin(UserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']

    fieldsets=(
        (None, {'fields' : ('email', 'name')}),
        ('permissions', {'fields' : ('is_active', 'is_staff', 'is_superuser')}),
        ('dates', {'fields' : ('last_login',)}),
    )

    readonly_fields=['last_login']


admin.site.register(models.User, UserModelAdmin)

