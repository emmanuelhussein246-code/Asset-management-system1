from django import forms
from django.contrib.auth.models import User
from .models import Asset, AssetCheckout, MaintenanceRecord, Department, StaffProfile


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'asset_name', 'asset_label', 'description', 'asset_type',
            'department', 'acquired_by_name', 'acquired_by_user',
            'acquisition_date', 'status', 'serial_number',
            'next_maintenance', 'notes',
        ]
        widgets = {
            'asset_name':       forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Dell Laptop 15 inch'}),
            'asset_label':      forms.TextInput(attrs={'class': 'form-input mono-input', 'placeholder': 'SPH-ELEC-0001'}),
            'description':      forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Condition, colour, specs, markings...'}),
            'asset_type':       forms.Select(attrs={'class': 'form-input'}),
            'department':       forms.Select(attrs={'class': 'form-input'}),
            'acquired_by_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full name of person who received asset'}),
            'acquired_by_user': forms.Select(attrs={'class': 'form-input'}),
            'acquisition_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'status':           forms.Select(attrs={'class': 'form-input'}),
            'serial_number':    forms.TextInput(attrs={'class': 'form-input mono-input', 'placeholder': 'Manufacturer serial (optional)'}),
            'next_maintenance': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'notes':            forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Any extra remarks'}),
        }


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = AssetCheckout
        fields = ['checked_out_by_name', 'checked_out_by_user', 'purpose', 'expected_return']
        widgets = {
            'checked_out_by_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full name'}),
            'checked_out_by_user': forms.Select(attrs={'class': 'form-input'}),
            'purpose':             forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Reason for taking the asset'}),
            'expected_return':     forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }


class CheckinForm(forms.Form):
    """Simple confirmation form for returning an asset."""
    confirm = forms.BooleanField(required=True, label='I confirm this asset has been returned to the hub.')


class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = ['title', 'details', 'status', 'assigned_to', 'scheduled_date', 'completed_date']
        widgets = {
            'title':          forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Screen repair, battery replacement'}),
            'details':        forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'status':         forms.Select(attrs={'class': 'form-input'}),
            'assigned_to':    forms.Select(attrs={'class': 'form-input'}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'completed_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }


class StaffProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name  = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-input'}))
    email      = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-input'}))
    username   = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-input'}))
    password   = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Leave blank to keep existing'}),
        help_text='Leave blank when editing to keep the current password.'
    )

    class Meta:
        model = StaffProfile
        fields = ['department', 'role', 'phone']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-input'}),
            'role':       forms.Select(attrs={'class': 'form-input'}),
            'phone':      forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+254 700 000 000'}),
        }
