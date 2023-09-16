from django.contrib import admin
from . import models
from django.contrib.auth.admin import UserAdmin

class UserModelAdmin(UserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']


admin.site.register(models.User, UserModelAdmin)

