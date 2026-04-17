from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone


class Department(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return self.name


class StaffProfile(models.Model):
    ROLE_CHOICES = [
        ('superadmin', 'Superadmin'),
        ('dept_head',  'Department Head'),
        ('staff',      'Staff'),
    ]
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    phone      = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Staff Profile'
        verbose_name_plural = 'Staff Profiles'

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_role_display()})"


label_validator = RegexValidator(
    regex=r'^SPH-\d{4}$',
    message='Label must follow: SPH-[NUMBER] e.g. SPH-0001'
)


class Asset(models.Model):
    TYPE_CHOICES = [
        ('electronics', 'Electronics'),
        ('furniture',   'Furniture'),
        ('equipment',   'Equipment'),
        ('stationery',  'Stationery'),
        ('vehicle',     'Vehicle'),
        ('facility',    'Facility'),
        ('other',       'Other'),
    ]
    STATUS_CHOICES = [
        ('available',      'Available'),
        ('in_use',         'In Use'),
        ('maintenance',    'Under Maintenance'),
        ('lost',           'Lost'),
        ('decommissioned', 'Decommissioned'),
    ]

    asset_name       = models.CharField(max_length=200)
    asset_label      = models.CharField(max_length=50, unique=True,
                                        help_text='Enter the label as printed on the physical asset')
    description      = models.TextField()
    asset_type       = models.CharField(max_length=20, choices=TYPE_CHOICES)
    department       = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='assets')
    acquired_by_name = models.CharField(max_length=200, help_text='Full name of person who acquired this asset')
    acquired_by_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='acquired_assets')
    acquisition_date = models.DateField()
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    serial_number    = models.CharField(max_length=100, blank=True)
    next_maintenance = models.DateField(null=True, blank=True)
    notes            = models.TextField(blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)
    registered_by    = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='registered_assets')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Asset'
        verbose_name_plural = 'Assets'

    def __str__(self):
        return f"{self.asset_label} — {self.asset_name}"

    @property
    def current_checkout(self):
        return self.checkouts.filter(returned_at__isnull=True).first()

    @property
    def is_overdue_maintenance(self):
        if self.next_maintenance:
            return self.next_maintenance < timezone.now().date()
        return False

    def get_status_color(self):
        return {
            'available':      'success',
            'in_use':         'info',
            'maintenance':    'warning',
            'lost':           'danger',
            'decommissioned': 'secondary',
        }.get(self.status, 'secondary')


class AssetCheckout(models.Model):
    asset                = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='checkouts')
    checked_out_by_name  = models.CharField(max_length=200)
    checked_out_by_user  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                              related_name='checkouts')
    purpose              = models.CharField(max_length=300, blank=True)
    checked_out_at       = models.DateTimeField(default=timezone.now)
    expected_return      = models.DateField(null=True, blank=True)
    returned_at          = models.DateTimeField(null=True, blank=True)
    logged_by            = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                              related_name='logged_checkouts')

    class Meta:
        ordering = ['-checked_out_at']
        verbose_name = 'Asset Checkout'
        verbose_name_plural = 'Asset Checkouts'

    def __str__(self):
        state = 'OUT' if not self.returned_at else 'RETURNED'
        return f"{self.asset.asset_label} [{state}] — {self.checked_out_by_name}"

    @property
    def is_returned(self):
        return self.returned_at is not None

    @property
    def is_overdue(self):
        if self.expected_return and not self.returned_at:
            return self.expected_return < timezone.now().date()
        return False


class MaintenanceRecord(models.Model):
    STATUS_CHOICES = [
        ('pending',     'Pending'),
        ('in_progress', 'In Progress'),
        ('done',        'Done'),
    ]
    asset          = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='maintenance_records')
    title          = models.CharField(max_length=200)
    details        = models.TextField(blank=True)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_to    = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='maintenance_tasks')
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    created_by     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='created_maintenance')

    class Meta:
        ordering = ['-scheduled_date']
        verbose_name = 'Maintenance Record'
        verbose_name_plural = 'Maintenance Records'

    def __str__(self):
        return f"{self.asset.asset_label} — {self.title} ({self.get_status_display()})"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('asset_created',     'Asset Created'),
        ('asset_updated',     'Asset Updated'),
        ('asset_deleted',     'Asset Deleted'),
        ('checkout',          'Asset Checked Out'),
        ('checkin',           'Asset Checked In'),
        ('maintenance_added', 'Maintenance Task Added'),
        ('status_changed',    'Status Changed'),
    ]
    action       = models.CharField(max_length=30, choices=ACTION_CHOICES)
    asset_label  = models.CharField(max_length=50, blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='audit_logs')
    department   = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    description  = models.TextField()
    timestamp    = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        default_permissions = ('view',)

    def __str__(self):
        user = self.performed_by.get_full_name() if self.performed_by else 'System'
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.get_action_display()} — {user}"

    def get_action_color(self):
        return {
            'asset_created':     'success',
            'asset_updated':     'info',
            'asset_deleted':     'danger',
            'checkout':          'warning',
            'checkin':           'success',
            'maintenance_added': 'secondary',
            'status_changed':    'info',
        }.get(self.action, 'secondary')
