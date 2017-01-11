from django.contrib import admin
from .models import UserPermission, AuthorizableProject, UserPermissionRequest, DataUseAgreement, DataUseAgreementSign


class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'permission')


class AuthorizableProjectAdmin(admin.ModelAdmin):
    list_display = ('project_key', 'name')


class UserPermissionRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'date_requested', 'request_granted', 'date_request_granted')


class DataUseAgreementAdmin(admin.ModelAdmin):
    list_display = ('name', 'project')


class DataUseAgreementSignAdmin(admin.ModelAdmin):
    list_display = ('data_use_agreement', 'user', 'date_signed')

admin.site.register(UserPermission, UserPermissionAdmin)
admin.site.register(AuthorizableProject, AuthorizableProjectAdmin)
admin.site.register(UserPermissionRequest, UserPermissionRequestAdmin)
admin.site.register(DataUseAgreement, DataUseAgreementAdmin)
admin.site.register(DataUseAgreementSign, DataUseAgreementSignAdmin)
