from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Assets
    path('assets/',                    views.asset_list,   name='asset_list'),
    path('assets/add/',                views.asset_add,    name='asset_add'),
    path('assets/<int:pk>/',           views.asset_detail, name='asset_detail'),
    path('assets/<int:pk>/edit/',      views.asset_edit,   name='asset_edit'),
    path('assets/<int:pk>/delete/',    views.asset_delete, name='asset_delete'),

    # Checkout / Check-in
    path('assets/<int:pk>/checkout/',              views.asset_checkout, name='asset_checkout'),
    path('checkout/<int:checkout_pk>/checkin/',    views.asset_checkin,  name='asset_checkin'),

    # Maintenance
    path('maintenance/',                           views.maintenance_list, name='maintenance_list'),
    path('assets/<int:asset_pk>/maintenance/add/', views.maintenance_add,  name='maintenance_add'),

    # Audit log
    path('audit/',  views.audit_log,  name='audit_log'),

    # Staff
    path('staff/',      views.staff_list, name='staff_list'),
    path('staff/add/',  views.staff_add,  name='staff_add'),
]
