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

    add_fieldsets=(
        (None,
            {'classes':('with',),
             'fields':('email',
                       'password1',
                       'password2',
                       'name',
                       'is_staff',
                       'is_superuser',
                       'is_active',
                       ),
                       }
        ),
    )


admin.site.register(models.User, UserModelAdmin)
admin.site.register(models.Tag)
admin.site.register(models.Recipe)
