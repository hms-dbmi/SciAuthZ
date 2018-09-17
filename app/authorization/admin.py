from django.contrib import admin
from .models import UserPermission

class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'item', 'permission', 'date_updated')

admin.site.register(UserPermission, UserPermissionAdmin)
