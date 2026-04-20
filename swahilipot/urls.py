from django.contrib import admin
from django.urls import path, include
from assets_app import views as app_views

urlpatterns = [
    # Login / Logout / Signup / Profile
    path('login/',  app_views.login_view,  name='login'),
    path('logout/', app_views.logout_view, name='logout'),
    path('signup/', app_views.signup_view, name='signup'),
    path('profile/', app_views.profile_view, name='profile'),

    # App routes
    path('', include('assets_app.urls')),

    # Django admin (restricted to superusers only — kept for DB-level access)
    path('django-admin/', admin.site.urls),
]
