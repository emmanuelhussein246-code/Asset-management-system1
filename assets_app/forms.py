from django import forms
from django.contrib.auth.models import User
from .models import Asset, AssetCheckout, MaintenanceRecord, Department, AssetType, StaffProfile


class AssetForm(forms.ModelForm):
    new_department = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Or type a new department name here'
        }),
        label='New Department (optional)',
        help_text='If the department does not exist, type its name here to create it'
    )

    class Meta:
        model = Asset
        fields = [
            'asset_name', 'asset_label', 'description', 'department', 'quantity',
            'serial_number', 'next_maintenance', 'notes',
        ]
        widgets = {
            'asset_name':       forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Dell Laptop 15 inch'}),
            'asset_label':      forms.TextInput(attrs={'class': 'form-input mono-input', 'placeholder': 'SPH-ELEC-0001'}),
            'description':      forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Condition, colour, specs, markings...'}),
            'department':       forms.Select(attrs={'class': 'form-input'}),
            'quantity':         forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Number of units received', 'min': 1}),
            'serial_number':    forms.TextInput(attrs={'class': 'form-input mono-input', 'placeholder': 'Manufacturer serial (optional)'}),
            'next_maintenance': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'notes':            forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Any extra remarks'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        department = cleaned_data.get('department')
        new_department = cleaned_data.get('new_department')

        if not department and not new_department:
            raise forms.ValidationError('Please select an existing department or create a new one.')

        return cleaned_data


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = AssetCheckout
        fields = [
            'checked_out_by_name', 'checked_out_by_user', 'department',
            'quantity', 'purpose', 'expected_return',
            'recipient_phone', 'recipient_email', 'recipient_kenyan_id',
        ]
        widgets = {
            'checked_out_by_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full name of person receiving asset'}),
            'checked_out_by_user': forms.Select(attrs={'class': 'form-input'}),
            'department':          forms.Select(attrs={'class': 'form-input'}),
            'quantity':            forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Number of units', 'min': 1}),
            'purpose':             forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Reason for taking the asset'}),
            'expected_return':     forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'recipient_phone':     forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Recipient phone number'}),
            'recipient_email':     forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Recipient email address'}),
            'recipient_kenyan_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Recipient Kenyan ID number'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show users with admin roles
        self.fields['checked_out_by_user'].queryset = User.objects.filter(
            profile__role__in=['superadmin', 'hr', 'admin'], profile__is_approved=True
        )


class CheckinForm(forms.Form):
    """Simple confirmation form for returning an asset."""
    confirm = forms.BooleanField(required=True, label='I confirm this asset has been returned to the hub.')


class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = ['title', 'broken_items', 'issue_details', 'items_to_fix', 'action_needed', 'reported_by', 'status', 'assigned_to', 'scheduled_date', 'completed_date']
        widgets = {
            'title':          forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Screen repair, battery replacement'}),
            'broken_items':   forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Describe the broken or damaged items'}),
            'issue_details':  forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'More details about the issue'}),
            'items_to_fix':   forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'List items that need to be fixed'}),
            'action_needed':  forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Actions required to fix the items'}),
            'reported_by':    forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Name of the person reporting'}),
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
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Set password (leave blank for staff)'}),
        help_text='Leave blank for staff members (no password needed).'
    )

    class Meta:
        model = StaffProfile
        fields = ['department', 'role', 'phone', 'kenyan_id', 'is_approved']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-input'}),
            'role':       forms.Select(attrs={'class': 'form-input'}),
            'phone':      forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+254 700 000 000'}),
            'kenyan_id':  forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 12345678'}),
        }


class ProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-input'}))
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-input'}))
    password = forms.CharField(
        required=False,
        min_length=6,
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Leave blank to keep existing'}),
        help_text='Enter a new password to change it.'
    )
    confirm_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm new password'})
    )
    role = forms.ChoiceField(choices=StaffProfile.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-input'}))

    class Meta:
        model = StaffProfile
        fields = ['role', 'phone', 'kenyan_id']
        widgets = {
            'role':       forms.Select(attrs={'class': 'form-input'}),
            'phone':      forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+254 700 000 000'}),
            'kenyan_id':  forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 12345678'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['username'].initial = self.instance.user.username
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password:
            if not confirm_password:
                raise forms.ValidationError('Please confirm your new password.')
            if password != confirm_password:
                raise forms.ValidationError('Passwords do not match.')
        return cleaned_data


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'}))
    last_name  = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'}))
    username   = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Choose a username'}))
    email      = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email Address'}))
    phone      = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+254 700 000 000'}))
    kenyan_id  = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Kenyan ID Number'}))
    role       = forms.ChoiceField(choices=StaffProfile.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-input'}), initial='staff')
    password   = forms.CharField(min_length=6, widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password (min 6 characters)'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm Password'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken. Please choose another.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data


class AssetTypeForm(forms.ModelForm):
    class Meta:
        model = AssetType
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Electronics, Furniture, Equipment'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Optional description'}),
        }


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. IT Department, Finance, HR'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Optional description of department responsibilities'}),
        }
