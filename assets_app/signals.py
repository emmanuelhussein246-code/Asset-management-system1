from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Asset, AssetCheckout, MaintenanceRecord, AuditLog

# Cache old status so we can detect status-only changes
_old_status_cache = {}


@receiver(pre_save, sender=Asset)
def cache_old_asset_status(sender, instance, **kwargs):
    """Store old status before save so we can compare after."""
    if instance.pk:
        try:
            _old_status_cache[instance.pk] = Asset.objects.get(pk=instance.pk).status
        except Asset.DoesNotExist:
            pass


@receiver(post_save, sender=Asset)
def log_asset_save(sender, instance, created, **kwargs):
    old_status = _old_status_cache.pop(instance.pk, None)

    if created:
        AuditLog.objects.create(
            action='asset_created',
            asset_label=instance.asset_label,
            performed_by=instance.registered_by,
            department=instance.department,
            description=(
                f"New asset registered: {instance.asset_label} — {instance.asset_name} "
                f"({instance.get_asset_type_display()}) assigned to {instance.department}. "
                f"Acquired by: {instance.acquired_by_name}."
            ),
        )
    elif old_status and old_status != instance.status:
        AuditLog.objects.create(
            action='status_changed',
            asset_label=instance.asset_label,
            department=instance.department,
            description=(
                f"Status of {instance.asset_label} ({instance.asset_name}) changed "
                f"from '{old_status}' to '{instance.status}'."
            ),
        )
    else:
        AuditLog.objects.create(
            action='asset_updated',
            asset_label=instance.asset_label,
            department=instance.department,
            description=f"Asset {instance.asset_label} ({instance.asset_name}) was updated.",
        )


@receiver(post_delete, sender=Asset)
def log_asset_delete(sender, instance, **kwargs):
    AuditLog.objects.create(
        action='asset_deleted',
        asset_label=instance.asset_label,
        department=instance.department,
        description=f"Asset {instance.asset_label} ({instance.asset_name}) was deleted from the system.",
    )


@receiver(post_save, sender=AssetCheckout)
def log_checkout_save(sender, instance, created, **kwargs):
    if created:
        AuditLog.objects.create(
            action='checkout',
            asset_label=instance.asset.asset_label,
            performed_by=instance.logged_by,
            department=instance.asset.department,
            description=(
                f"{instance.asset.asset_label} ({instance.asset.asset_name}) checked out by "
                f"{instance.checked_out_by_name}. Purpose: {instance.purpose or 'Not specified'}. "
                f"Expected return: {instance.expected_return or 'Not set'}."
            ),
        )
        # Auto-update asset status to in_use
        Asset.objects.filter(pk=instance.asset.pk).update(status='in_use')

    elif instance.returned_at:
        AuditLog.objects.create(
            action='checkin',
            asset_label=instance.asset.asset_label,
            performed_by=instance.logged_by,
            department=instance.asset.department,
            description=(
                f"{instance.asset.asset_label} ({instance.asset.asset_name}) returned by "
                f"{instance.checked_out_by_name} on {instance.returned_at:%Y-%m-%d %H:%M}."
            ),
        )
        # Auto-update asset status based on remaining active checkouts
        active_exists = AssetCheckout.objects.filter(
            asset=instance.asset,
            returned_at__isnull=True
        ).exclude(pk=instance.pk).exists()
        new_status = 'in_use' if active_exists else 'available'
        Asset.objects.filter(pk=instance.asset.pk).update(status=new_status)


@receiver(post_save, sender=MaintenanceRecord)
def log_maintenance_save(sender, instance, created, **kwargs):
    if created:
        AuditLog.objects.create(
            action='maintenance_added',
            asset_label=instance.asset.asset_label,
            performed_by=instance.created_by,
            department=instance.asset.department,
            description=(
                f"Maintenance task '{instance.title}' added for {instance.asset.asset_label} "
                f"({instance.asset.asset_name}). Scheduled: {instance.scheduled_date}. "
                f"Assigned to: {instance.assigned_to.get_full_name() if instance.assigned_to else 'Unassigned'}."
            ),
        )
