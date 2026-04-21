from django.contrib import admin
from .models import Department, AssetType, StaffProfile, Asset, AssetCheckout, MaintenanceRecord, AuditLog


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display  = ('name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(AssetType)
class AssetTypeAdmin(admin.ModelAdmin):
    list_display  = ('name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display   = ('user', 'department', 'role', 'phone', 'is_approved', 'created_at')
    list_filter    = ('role', 'department', 'is_approved')
    search_fields  = ('user__first_name', 'user__last_name', 'user__email', 'phone')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Staff Info', {'fields': ('role', 'department', 'phone', 'kenyan_id')}),
        ('Approval', {'fields': ('is_approved',)}),
        ('Timestamps', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display   = ('asset_label', 'asset_name', 'asset_type', 'department', 'acquired_by_name', 'status', 'quantity', 'current_holder', 'created_at')
    list_filter    = ('status', 'asset_type', 'department')
    search_fields  = ('asset_label', 'asset_name', 'acquired_by_name', 'serial_number')
    readonly_fields = ('created_at', 'updated_at', 'registered_by')
    date_hierarchy = 'acquisition_date'
    fieldsets = (
        ('Basic Info', {'fields': ('asset_label', 'asset_name', 'asset_type', 'description')}),
        ('Department & Ownership', {'fields': ('department', 'acquired_by_name', 'acquisition_date')}),
        ('Status & Location', {'fields': ('status', 'quantity', 'current_holder', 'recipient')}),
        ('Technical Details', {'fields': ('serial_number', 'notes')}),
        ('Maintenance', {'fields': ('next_maintenance',)}),
        ('Metadata', {'fields': ('created_at', 'updated_at', 'registered_by'), 'classes': ('collapse',)}),
    )


@admin.register(AssetCheckout)
class AssetCheckoutAdmin(admin.ModelAdmin):
    list_display  = ('asset', 'checked_out_by_name', 'quantity', 'checked_out_at', 'expected_return', 'returned_at')
    list_filter   = ('asset__department', 'checked_out_at')
    search_fields = ('asset__asset_label', 'checked_out_by_name', 'recipient_email')
    readonly_fields = ('checked_out_at',)
    fieldsets = (
        ('Asset', {'fields': ('asset',)}),
        ('Checkout By', {'fields': ('checked_out_by_name', 'checked_out_by_user', 'logged_by')}),
        ('Recipient Info', {'fields': ('recipient_phone', 'recipient_email', 'recipient_kenyan_id')}),
        ('Details', {'fields': ('quantity', 'purpose', 'department')}),
        ('Dates', {'fields': ('checked_out_at', 'expected_return', 'returned_at')}),
    )


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display  = ('asset', 'title', 'status', 'scheduled_date', 'assigned_to', 'completed_date')
    list_filter   = ('status', 'scheduled_date')
    search_fields = ('asset__asset_label', 'title', 'assigned_to')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Maintenance Info', {'fields': ('asset', 'title', 'description')}),
        ('Status & Assignment', {'fields': ('status', 'assigned_to')}),
        ('Dates', {'fields': ('scheduled_date', 'completed_date')}),
        ('Metadata', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )


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
