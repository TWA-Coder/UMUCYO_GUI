from django.contrib import admin
from .models import Role, UserRole, RoleOperation, SoapRequestLog

class RoleOperationInline(admin.TabularInline):
    model = RoleOperation
    extra = 1

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [RoleOperationInline]

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'assigned_at')
    list_filter = ('role',)
    search_fields = ('user__username', 'role__name')

@admin.register(RoleOperation)
class RoleOperationAdmin(admin.ModelAdmin):
    list_display = ('role', 'operation_name', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('operation_name',)

@admin.register(SoapRequestLog)
class SoapRequestLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'operation', 'user', 'status', 'duration')
    list_filter = ('status', 'operation', 'timestamp')
    search_fields = ('operation', 'user__username', 'request_payload')
    readonly_fields = ('timestamp', 'operation', 'user', 'request_payload', 'response_payload', 'status', 'duration', 'error_message')

    def has_add_permission(self, request):
        return False
