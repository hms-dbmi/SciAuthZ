from django.contrib import admin
from .models import UserPermission

# Register your models here.
class UserPermissionAdmin(admin.ModelAdmin):
    pass

admin.site.register(UserPermission, UserPermissionAdmin)