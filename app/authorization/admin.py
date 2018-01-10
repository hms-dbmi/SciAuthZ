from django.contrib import admin
from .models import UserPermission, UserPermissionRequest

class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'permission')

class UserPermissionRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'date_requested', 'request_granted', 'date_request_granted')

admin.site.register(UserPermission, UserPermissionAdmin)
admin.site.register(UserPermissionRequest, UserPermissionRequestAdmin)
