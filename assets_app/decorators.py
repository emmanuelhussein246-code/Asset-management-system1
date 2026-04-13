from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """
    Restricts a view to authenticated staff users only.
    Redirects unauthenticated users to the login page.
    Redirects non-staff users with an 'Access denied' message.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_staff and not request.user.is_superuser:
            messages.error(request, 'Access denied. This system is for authorised staff only.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper
