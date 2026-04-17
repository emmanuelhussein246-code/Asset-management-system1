from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q

from .decorators import admin_required
from .models import Asset, AssetCheckout, MaintenanceRecord, AuditLog, Department, StaffProfile
from .forms import AssetForm, CheckoutForm, CheckinForm, MaintenanceForm, StaffProfileForm


# ──────────────────────────────────────────────
#  AUTH
# ──────────────────────────────────────────────

def login_view(request):
    """
    Custom login — only is_staff or is_superuser users are allowed in.
    Regular User accounts are rejected even if credentials are correct.
    """
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_staff or user.is_superuser:
                login(request, user)
                return redirect(request.GET.get('next', 'dashboard'))
            else:
                messages.error(request, 'Your account does not have admin access.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'assets_app/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


# ──────────────────────────────────────────────
#  DASHBOARD
# ──────────────────────────────────────────────

@admin_required
def dashboard(request):
    total_assets      = Asset.objects.count()
    available         = Asset.objects.filter(status='available').count()
    in_use            = Asset.objects.filter(status='in_use').count()
    maintenance_count = Asset.objects.filter(status='maintenance').count()
    lost_count        = Asset.objects.filter(status='lost').count()
    overdue_maintenance = Asset.objects.filter(
        next_maintenance__lt=timezone.now().date()
    ).exclude(status='decommissioned').count()

    # Get filtered asset lists for each tab
    all_assets = Asset.objects.select_related('department', 'acquired_by_user')[:10]
    available_assets = Asset.objects.filter(status='available').select_related('department')[:10]
    in_use_assets = Asset.objects.filter(status='in_use').select_related('department').prefetch_related('checkouts__checked_out_by_user')[:10]
    maintenance_assets = Asset.objects.filter(status='maintenance').select_related('department')[:10]
    lost_assets = Asset.objects.filter(status='lost').select_related('department')[:10]
    overdue_assets = Asset.objects.filter(
        next_maintenance__lt=timezone.now().date()
    ).exclude(status='decommissioned').select_related('department')[:10]

    dept_stats = Department.objects.annotate(
        total=Count('assets'),
        in_use=Count('assets', filter=Q(assets__status='in_use')),
    )

    recent_logs   = AuditLog.objects.select_related('performed_by', 'department')[:10]
    recent_assets = Asset.objects.select_related('department')[:5]

    context = {
        'total_assets':       total_assets,
        'available':          available,
        'in_use':             in_use,
        'maintenance_count':  maintenance_count,
        'lost_count':         lost_count,
        'overdue_maintenance': overdue_maintenance,
        'all_assets':         all_assets,
        'available_assets':   available_assets,
        'in_use_assets':      in_use_assets,
        'maintenance_assets': maintenance_assets,
        'lost_assets':        lost_assets,
        'overdue_assets':     overdue_assets,
        'dept_stats':         dept_stats,
        'recent_logs':        recent_logs,
        'recent_assets':      recent_assets,
    }
    return render(request, 'assets_app/dashboard.html', context)


# ──────────────────────────────────────────────
#  ASSETS — CRUD
# ──────────────────────────────────────────────

@admin_required
def asset_list(request):
    query      = request.GET.get('q', '')
    dept_id    = request.GET.get('dept', '')
    type_filter = request.GET.get('type', '')
    status_filter = request.GET.get('status', '')

    assets = Asset.objects.select_related('department', 'acquired_by_user')

    if query:
        assets = assets.filter(
            Q(asset_name__icontains=query) |
            Q(asset_label__icontains=query) |
            Q(acquired_by_name__icontains=query)
        )
    if dept_id:
        assets = assets.filter(department_id=dept_id)
    if type_filter:
        assets = assets.filter(asset_type=type_filter)
    if status_filter:
        assets = assets.filter(status=status_filter)

    departments = Department.objects.all()
    context = {
        'assets':        assets,
        'departments':   departments,
        'query':         query,
        'dept_id':       dept_id,
        'type_filter':   type_filter,
        'status_filter': status_filter,
        'type_choices':  Asset.TYPE_CHOICES,
        'status_choices': Asset.STATUS_CHOICES,
    }
    return render(request, 'assets_app/asset_list.html', context)


@admin_required
def asset_add(request):
    form = AssetForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        asset = form.save(commit=False)
        asset.registered_by = request.user
        asset.save()
        messages.success(request, f'Asset {asset.asset_label} registered successfully.')
        return redirect('asset_detail', pk=asset.pk)
    return render(request, 'assets_app/asset_form.html', {'form': form, 'title': 'Add New Asset'})


@admin_required
def asset_detail(request, pk):
    asset       = get_object_or_404(Asset, pk=pk)
    checkouts   = asset.checkouts.select_related('checked_out_by_user', 'logged_by').order_by('-checked_out_at')
    maintenance = asset.maintenance_records.select_related('assigned_to', 'created_by')
    active_checkout = checkouts.filter(returned_at__isnull=True).first()

    context = {
        'asset':          asset,
        'checkouts':      checkouts,
        'maintenance':    maintenance,
        'active_checkout': active_checkout,
    }
    return render(request, 'assets_app/asset_detail.html', context)


@admin_required
def asset_edit(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    form  = AssetForm(request.POST or None, instance=asset)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Asset {asset.asset_label} updated.')
        return redirect('asset_detail', pk=asset.pk)
    return render(request, 'assets_app/asset_form.html', {'form': form, 'title': f'Edit {asset.asset_label}', 'asset': asset})


@admin_required
def asset_delete(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        label = asset.asset_label
        asset.delete()
        messages.success(request, f'Asset {label} has been deleted.')
        return redirect('asset_list')
    return render(request, 'assets_app/asset_confirm_delete.html', {'asset': asset})


# ──────────────────────────────────────────────
#  CHECKOUT / CHECK-IN
# ──────────────────────────────────────────────

@admin_required
def asset_checkout(request, pk):
    asset = get_object_or_404(Asset, pk=pk)

    if asset.status == 'in_use':
        messages.warning(request, f'{asset.asset_label} is already checked out.')
        return redirect('asset_detail', pk=pk)

    form = CheckoutForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        checkout = form.save(commit=False)
        checkout.asset     = asset
        checkout.logged_by = request.user
        checkout.save()
        messages.success(request, f'{asset.asset_label} checked out to {checkout.checked_out_by_name}.')
        return redirect('asset_detail', pk=pk)

    return render(request, 'assets_app/checkout_form.html', {'form': form, 'asset': asset})


@admin_required
def asset_checkin(request, checkout_pk):
    checkout = get_object_or_404(AssetCheckout, pk=checkout_pk, returned_at__isnull=True)
    asset    = checkout.asset

    if request.method == 'POST':
        checkout.returned_at = timezone.now()
        checkout.logged_by   = request.user
        checkout.save()
        messages.success(request, f'{asset.asset_label} has been returned and marked available.')
        return redirect('asset_detail', pk=asset.pk)

    return render(request, 'assets_app/checkin_confirm.html', {'checkout': checkout, 'asset': asset})


# ──────────────────────────────────────────────
#  MAINTENANCE
# ──────────────────────────────────────────────

@admin_required
def maintenance_list(request):
    records = MaintenanceRecord.objects.select_related('asset', 'asset__department', 'assigned_to')
    status_filter = request.GET.get('status', '')
    if status_filter:
        records = records.filter(status=status_filter)

    overdue = records.filter(
        scheduled_date__lt=timezone.now().date()
    ).exclude(status='done')

    context = {
        'records':       records,
        'overdue':       overdue,
        'status_filter': status_filter,
        'status_choices': MaintenanceRecord.STATUS_CHOICES,
        'today':         timezone.now().date(),
    }
    return render(request, 'assets_app/maintenance_list.html', context)


@admin_required
def maintenance_add(request, asset_pk):
    asset = get_object_or_404(Asset, pk=asset_pk)
    form  = MaintenanceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        record = form.save(commit=False)
        record.asset      = asset
        record.created_by = request.user
        record.save()
        messages.success(request, f'Maintenance task added for {asset.asset_label}.')
        return redirect('asset_detail', pk=asset.pk)
    return render(request, 'assets_app/maintenance_form.html', {'form': form, 'asset': asset})


# ──────────────────────────────────────────────
#  AUDIT LOG
# ──────────────────────────────────────────────

@admin_required
def audit_log(request):
    logs  = AuditLog.objects.select_related('performed_by', 'department')
    query = request.GET.get('q', '')
    action_filter = request.GET.get('action', '')

    if query:
        logs = logs.filter(
            Q(asset_label__icontains=query) |
            Q(description__icontains=query) |
            Q(performed_by__first_name__icontains=query) |
            Q(performed_by__last_name__icontains=query)
        )
    if action_filter:
        logs = logs.filter(action=action_filter)

    context = {
        'logs':           logs,
        'query':          query,
        'action_filter':  action_filter,
        'action_choices': AuditLog.ACTION_CHOICES,
    }
    return render(request, 'assets_app/audit_log.html', context)


# ──────────────────────────────────────────────
#  STAFF MANAGEMENT
# ──────────────────────────────────────────────

@admin_required
def staff_list(request):
    profiles = StaffProfile.objects.select_related('user', 'department').order_by('user__last_name')
    return render(request, 'assets_app/staff_list.html', {'profiles': profiles})


@admin_required
def staff_add(request):
    form = StaffProfileForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            email=form.cleaned_data['email'],
            is_staff=True,
        )
        profile = form.save(commit=False)
        profile.user = user
        profile.save()
        messages.success(request, f'Staff member {user.get_full_name()} created.')
        return redirect('staff_list')
    return render(request, 'assets_app/staff_form.html', {'form': form, 'title': 'Add Staff Member'})
