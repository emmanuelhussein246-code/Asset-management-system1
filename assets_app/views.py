from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .decorators import admin_required
from .models import Asset, AssetCheckout, MaintenanceRecord, AuditLog, Department, AssetType, StaffProfile
from .forms import AssetForm, CheckoutForm, CheckinForm, MaintenanceForm, StaffProfileForm, SignupForm, ProfileForm, AssetTypeForm, DepartmentForm


# ──────────────────────────────────────────────
#  AUTH
# ──────────────────────────────────────────────

def login_view(request):
    """
    Custom login — only approved staff users are allowed in.
    """
    if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.is_approved:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser or (hasattr(user, 'profile') and user.profile.is_approved):
                login(request, user)
                return redirect(request.GET.get('next', 'dashboard'))
            else:
                messages.error(request, 'Your account is not approved yet.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'assets_app/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


def signup_view(request):
    """
    Signup view — limited to 7 approved users max.
    """
    if StaffProfile.objects.filter(is_approved=True).count() >= 7:
        messages.error(request, 'Maximum number of approved users reached. Cannot create new accounts.')
        return redirect('login')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username'].strip()
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            kenyan_id = form.cleaned_data['kenyan_id']
            role = form.cleaned_data['role']
            password = form.cleaned_data['password']

            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists. Please choose another.')
                return redirect('signup')

            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                is_staff=True  # allow login access
            )

            StaffProfile.objects.create(
                user=user,
                role=role,
                phone=phone,
                kenyan_id=kenyan_id,
                is_approved=False  # pending approval
            )

            messages.success(request, f'Account created successfully. Pending approval by admin.')
            return redirect('login')
    else:
        form = SignupForm()

    return render(request, 'assets_app/signup.html', {'form': form})


@login_required
def profile_view(request):
    profile = get_object_or_404(StaffProfile, user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            user = request.user
            user.username = form.cleaned_data['username']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            if form.cleaned_data.get('password'):
                user.set_password(form.cleaned_data['password'])
            user.save()

            profile = form.save(commit=False)
            profile.user = user
            profile.save()

            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile, user=request.user)

    return render(request, 'assets_app/profile.html', {'form': form})


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
        
        # Handle new department creation
        new_department_name = form.cleaned_data.get('new_department')
        if new_department_name:
            department, created = Department.objects.get_or_create(name=new_department_name.strip())
            asset.department = department
        
        # Auto-set fields
        asset.acquisition_date = timezone.now()
        asset.status = 'available'
        asset.acquired_by_name = request.user.get_full_name()
        asset.acquired_by_user = request.user
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

    profile = getattr(request.user, 'profile', None)
    # The 1-day lock applies to everyone except superadmins and HR
    can_edit_after_day = request.user.is_superuser or (profile and profile.role in ['superadmin', 'hr'])
    
    if request.method == 'POST' and form.is_valid():
        if asset.created_at + timedelta(days=1) < timezone.now() and not can_edit_after_day:
            messages.error(request, 'This asset can only be edited within one day of registration.')
            return redirect('asset_detail', pk=asset.pk)

        asset = form.save(commit=False)
        
        # Handle new department creation
        new_department_name = form.cleaned_data.get('new_department')
        if new_department_name:
            department, created = Department.objects.get_or_create(name=new_department_name.strip())
            asset.department = department
        
        asset.save()
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

    if asset.status not in ['available', 'in_use']:
        messages.warning(request, f'{asset.asset_label} is not available for checkout.')
        return redirect('asset_detail', pk=pk)

    available_qty = asset.available_quantity
    if available_qty == 0:
        messages.warning(request, f'No available units left for {asset.asset_label}.')
        return redirect('asset_detail', pk=pk)

    form = CheckoutForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        checkout = form.save(commit=False)
        checkout.asset     = asset
        checkout.logged_by = request.user
 main
        if checkout.quantity > available_qty:
            form.add_error('quantity', f'Only {available_qty} unit(s) are available for this asset.')
        else:
            checkout.save()
            asset.current_holder = checkout.checked_out_by_name
            asset.save()
            messages.success(request, f'{asset.asset_label} checked out to {checkout.checked_out_by_name}.')
            return redirect('asset_detail', pk=pk)

        checkout.save()
        
        # Send email notification
        try:
            recipient_email = None
            recipient_name = checkout.checked_out_by_name
            
            # Get email from user account or manual entry
            if checkout.checked_out_by_user and checkout.checked_out_by_user.email:
                recipient_email = checkout.checked_out_by_user.email
            elif checkout.email:
                recipient_email = checkout.email
            
            # Send email if we have a valid email address
            if recipient_email:
                # Prepare email context
                context = {
                    'checkout': checkout,
                    'asset': asset,
                }
                
                # Render email templates
                html_message = render_to_string('assets_app/emails/asset_assigned_email.html', context)
                text_message = render_to_string('assets_app/emails/asset_assigned_email.txt', context)
                
                # Send email
                send_mail(
                    subject=f'Asset Assigned: {asset.asset_label}',
                    message=text_message,
                    from_email=None,  # Will use DEFAULT_FROM_EMAIL in production
                    recipient_list=[recipient_email],
                    html_message=html_message,
                    fail_silently=True
                )
                
                messages.success(request, f'{asset.asset_label} checked out to {checkout.checked_out_by_name}. Email notification sent to {recipient_email}.')
            else:
                messages.success(request, f'{asset.asset_label} checked out to {checkout.checked_out_by_name}. No email notification sent - no email provided.')
        except Exception as e:
            messages.warning(request, f'Asset checked out but email notification failed: {str(e)}')
        
        return redirect('asset_detail', pk=pk)
 main

    return render(request, 'assets_app/checkout_form.html', {
        'form': form,
        'asset': asset,
        'available_qty': available_qty,
    })


@admin_required
def asset_checkin(request, checkout_pk):
    checkout = get_object_or_404(AssetCheckout, pk=checkout_pk, returned_at__isnull=True)
    asset    = checkout.asset

    if request.method == 'POST':
        checkout.returned_at = timezone.now()
        checkout.logged_by   = request.user
        checkout.save()
 main
        # Clear current_holder if no active checkouts
        if asset.checkouts.filter(returned_at__isnull=True).count() == 0:
            asset.current_holder = ''
            asset.save()
        messages.success(request, f'{asset.asset_label} has been returned and marked available.')

        
        # Send email notification for asset return
        try:
            recipient_email = None
            recipient_name = checkout.checked_out_by_name
            
            # Get email from user account or manual entry
            if checkout.checked_out_by_user and checkout.checked_out_by_user.email:
                recipient_email = checkout.checked_out_by_user.email
            elif checkout.email:
                recipient_email = checkout.email
            
            # Send email if we have a valid email address
            if recipient_email:
                # Prepare email context
                context = {
                    'checkout': checkout,
                    'asset': asset,
                }
                
                # Render email templates
                html_message = render_to_string('assets_app/emails/asset_returned_email.html', context)
                text_message = render_to_string('assets_app/emails/asset_returned_email.txt', context)
                
                # Send email
                send_mail(
                    subject=f'Asset Returned: {asset.asset_label}',
                    message=text_message,
                    from_email=None,  # Will use DEFAULT_FROM_EMAIL in production
                    recipient_list=[recipient_email],
                    html_message=html_message,
                    fail_silently=True
                )
                
                messages.success(request, f'{asset.asset_label} has been returned and marked available. Email notification sent to {recipient_email}.')
            else:
                messages.success(request, f'{asset.asset_label} has been returned and marked available. No email notification sent - no email provided.')
        except Exception as e:
            messages.warning(request, f'Asset returned but email notification failed: {str(e)}')
        
main
        return redirect('asset_detail', pk=asset.pk)

    return render(request, 'assets_app/checkin_confirm.html', {'checkout': checkout, 'asset': asset})


@admin_required
def checkout_list(request):
    """Display all asset checkouts/distributions in a table."""
    # Get all checkouts for display
    all_checkouts = AssetCheckout.objects.select_related(
        'asset', 'asset__department', 'checked_out_by_user', 'department', 'logged_by'
    ).order_by('-checked_out_at')
    
    # Filter by status for the main display
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        checkouts = all_checkouts.filter(returned_at__isnull=True)
    elif status_filter == 'returned':
        checkouts = all_checkouts.filter(returned_at__isnull=False)
    else:
        checkouts = all_checkouts
    
    # Filter by department
    dept_filter = request.GET.get('department', '')
    if dept_filter:
        checkouts = checkouts.filter(department__id=dept_filter)
    
    # Split the filtered list into active and returned groups for display.
    if status_filter == 'active':
        active_checkouts = checkouts
        returned_checkouts = AssetCheckout.objects.none()
    elif status_filter == 'returned':
        active_checkouts = AssetCheckout.objects.none()
        returned_checkouts = checkouts
    else:
        active_checkouts = checkouts.filter(returned_at__isnull=True)
        returned_checkouts = checkouts.filter(returned_at__isnull=False)
    
    # Calculate statistics based on the current filtered selection.
    active_checkouts_count = active_checkouts.count()
    returned_checkouts_count = returned_checkouts.count()
    
    context = {
        'checkouts': checkouts,
        'active_checkouts': active_checkouts,
        'returned_checkouts': returned_checkouts,
        'status_filter': status_filter,
        'dept_filter': dept_filter,
        'departments': Department.objects.all(),
        'today': timezone.now().date(),
        'active_checkouts_count': active_checkouts_count,
        'returned_checkouts_count': returned_checkouts_count,
    }
    return render(request, 'assets_app/checkout_list.html', context)


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
        password = form.cleaned_data.get('password')
        if not password:
            # For staff, set unusable password
            password = None
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=password,
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


@admin_required
def staff_edit(request, pk):
    profile = get_object_or_404(StaffProfile, pk=pk)
    form = StaffProfileForm(request.POST or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        password = form.cleaned_data.get('password')
        if password:
            profile.user.set_password(password)
            profile.user.save()
        form.save()
        messages.success(request, f'Staff member {profile.user.get_full_name()} updated.')
        return redirect('staff_list')
    return render(request, 'assets_app/staff_form.html', {'form': form, 'title': 'Edit Staff Member'})


@admin_required
def staff_approve(request, pk):
    profile = get_object_or_404(StaffProfile, pk=pk)
    if request.method == 'POST':
        profile.is_approved = True
        profile.save()
        messages.success(request, f'{profile.user.get_full_name()} has been approved.')
        return redirect('staff_list')
    return redirect('staff_list')


# ──────────────────────────────────────────────
#  ASSET TYPES MANAGEMENT
# ──────────────────────────────────────────────

@admin_required
def asset_types_list(request):
    """List all asset types."""
    asset_types = AssetType.objects.all()
    context = {
        'asset_types': asset_types,
    }
    return render(request, 'assets_app/asset_types_list.html', context)


@admin_required
def asset_type_add(request):
    """Add a new asset type."""
    form = AssetTypeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Asset type "{form.cleaned_data["name"]}" created.')
        return redirect('asset_types_list')
    return render(request, 'assets_app/asset_type_form.html', {'form': form, 'title': 'Add Asset Type'})


@admin_required
def asset_type_edit(request, pk):
    """Edit an asset type."""
    asset_type = get_object_or_404(AssetType, pk=pk)
    form = AssetTypeForm(request.POST or None, instance=asset_type)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Asset type "{asset_type.name}" updated.')
        return redirect('asset_types_list')
    return render(request, 'assets_app/asset_type_form.html', {'form': form, 'title': f'Edit {asset_type.name}', 'asset_type': asset_type})


@admin_required
def asset_type_delete(request, pk):
    """Delete an asset type."""
    asset_type = get_object_or_404(AssetType, pk=pk)
    if request.method == 'POST':
        name = asset_type.name
        asset_type.delete()
        messages.success(request, f'Asset type "{name}" deleted.')
        return redirect('asset_types_list')
    return render(request, 'assets_app/asset_type_confirm_delete.html', {'asset_type': asset_type})


@admin_required
def clear_all_data(request):
    """
    Clear all data from the system.
    Only superadmins are allowed to perform this action.
    The current user is preserved to avoid logout and lockout.
    """
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'superadmin':
        messages.error(request, 'Access denied. Only Superadmins can clear all system data.')
        return redirect('dashboard')

    if request.method == 'POST':
        confirmation = request.POST.get('confirm', '').lower()
        if confirmation == 'yes':
            # 1. Delete asset-related records
            AssetCheckout.objects.all().delete()
            MaintenanceRecord.objects.all().delete()
            AuditLog.objects.all().delete()
            
            # 2. Delete Assets, Types, and Departments
            Asset.objects.all().delete()
            AssetType.objects.all().delete()
            # We exclude the current user's department if they are assigned to one? 
            # No, user wants to "start afresh", so even departments should go.
            # But wait, if we delete the department, the current user's profile.department will be null.
            Department.objects.all().delete()
            
            # 3. Delete other users and profiles
            # Preserve current user and their profile
            current_user_id = request.user.pk
            
            # Delete other staff profiles
            StaffProfile.objects.exclude(user_id=current_user_id).delete()
            
            # Delete other users
            User.objects.exclude(pk=current_user_id).delete()
            
            messages.success(request, 'All data has been cleared successfully. You have been kept logged in to start afresh.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Confirmation failed. No data was deleted.')
            return redirect('clear_all_data')
    return render(request, 'assets_app/clear_data_confirm.html')


@login_required
def delete_all_data_in_department(request):
    """Delete all data in the user's department. Only for users with department and admin role."""
    if not hasattr(request.user, 'profile') or not request.user.profile.department:
        messages.error(request, 'You must be assigned to a department to perform this action.')
        return redirect('dashboard')
    
    profile = request.user.profile
    if profile.role != 'superadmin':
        messages.error(request, 'Access denied. Only superadmins can perform bulk data deletion.')
        return redirect('dashboard')
    
    department = profile.department
    
    if request.method == 'POST':
        confirmation = request.POST.get('confirm', '').lower()
        if confirmation == 'yes':
            # Delete all data in the department
            assets_deleted = Asset.objects.filter(department=department).delete()
            checkouts_deleted = AssetCheckout.objects.filter(department=department).delete()
            maintenance_deleted = MaintenanceRecord.objects.filter(asset__department=department).delete()
            messages.success(request, f'All data in {department.name} has been deleted successfully.')
            return redirect('asset_list')
        else:
            messages.error(request, 'Confirmation failed. No data was deleted.')
            return redirect('delete_all_data_in_department')
    
    assets_count = Asset.objects.filter(department=department).count()
    checkouts_count = AssetCheckout.objects.filter(department=department).count()
    maintenance_count = MaintenanceRecord.objects.filter(asset__department=department).count()
    context = {
        'department': department,
        'assets_count': assets_count,
        'checkouts_count': checkouts_count,
        'maintenance_count': maintenance_count,
    }
    return render(request, 'assets_app/delete_data_department_confirm.html', context)


# ──────────────────────────────────────────────
#  DEPARTMENT MANAGEMENT
# ──────────────────────────────────────────────

@admin_required
def departments_list(request):
    """List all departments."""
    departments = Department.objects.all()
    context = {
        'departments': departments,
    }
    return render(request, 'assets_app/departments_list.html', context)


@admin_required
def department_add(request):
    """Add a new department."""
    form = DepartmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Department "{form.cleaned_data["name"]}" created.')
        return redirect('departments_list')
    return render(request, 'assets_app/department_form.html', {'form': form, 'title': 'Add Department'})


@admin_required
def department_edit(request, pk):
    """Edit a department."""
    department = get_object_or_404(Department, pk=pk)
    form = DepartmentForm(request.POST or None, instance=department)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Department "{department.name}" updated.')
        return redirect('departments_list')
    return render(request, 'assets_app/department_form.html', {'form': form, 'title': f'Edit {department.name}', 'department': department})


@admin_required
def department_delete(request, pk):
    """Delete a department."""
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        name = department.name
        department.delete()
        messages.success(request, f'Department "{name}" deleted.')
        return redirect('departments_list')
    return render(request, 'assets_app/department_confirm_delete.html', {'department': department})
