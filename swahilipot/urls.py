from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from assets_app import views as app_views

urlpatterns = [
    # Login / Logout
    path('login/',  app_views.login_view,  name='login'),
    path('logout/', app_views.logout_view, name='logout'),

    # App routes
    path('', include('assets_app.urls')),

    # Django admin (restricted to superusers only — kept for DB-level access)
    path('django-admin/', admin.site.urls),
]
