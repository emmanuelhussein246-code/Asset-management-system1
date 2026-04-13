from django.contrib import admin
from .models import Department, StaffProfile, Asset, AssetCheckout, MaintenanceRecord, AuditLog


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display  = ('name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'department', 'role', 'phone', 'created_at')
    list_filter   = ('role', 'department')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display   = ('asset_label', 'asset_name', 'asset_type', 'department', 'acquired_by_name', 'status', 'created_at')
    list_filter    = ('status', 'asset_type', 'department')
    search_fields  = ('asset_label', 'asset_name', 'acquired_by_name', 'serial_number')
    readonly_fields = ('created_at', 'updated_at', 'registered_by')
    date_hierarchy = 'acquisition_date'


@admin.register(AssetCheckout)
class AssetCheckoutAdmin(admin.ModelAdmin):
    list_display  = ('asset', 'checked_out_by_name', 'checked_out_at', 'expected_return', 'returned_at')
    list_filter   = ('asset__department',)
    search_fields = ('asset__asset_label', 'checked_out_by_name')
    readonly_fields = ('checked_out_at',)


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display  = ('asset', 'title', 'status', 'scheduled_date', 'assigned_to', 'completed_date')
    list_filter   = ('status',)
    search_fields = ('asset__asset_label', 'title')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display  = ('timestamp', 'action', 'asset_label', 'performed_by', 'department')
    list_filter   = ('action', 'department')
    search_fields = ('asset_label', 'description')
    readonly_fields = ('timestamp', 'action', 'asset_label', 'performed_by', 'department', 'description')

    def has_add_permission(self, request):
        return False  # Audit logs are system-generated only

    def has_change_permission(self, request, obj=None):
        return False  # Immutable

    def has_delete_permission(self, request, obj=None):
        return False  # Cannot delete audit logs
