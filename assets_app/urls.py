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
    path('checkout/',                              views.checkout_list,  name='checkout_list'),
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
    path('staff/<int:pk>/edit/',  views.staff_edit,  name='staff_edit'),
    path('staff/<int:pk>/approve/',  views.staff_approve,  name='staff_approve'),

    # Asset Types
    path('asset-types/',                       views.asset_types_list,     name='asset_types_list'),
    path('asset-types/add/',                   views.asset_type_add,       name='asset_type_add'),
    path('asset-types/<int:pk>/edit/',         views.asset_type_edit,      name='asset_type_edit'),
    path('asset-types/<int:pk>/delete/',       views.asset_type_delete,    name='asset_type_delete'),

    # Departments
    path('departments/',                       views.departments_list,     name='departments_list'),
    path('departments/add/',                   views.department_add,       name='department_add'),
    path('departments/<int:pk>/edit/',         views.department_edit,      name='department_edit'),
    path('departments/<int:pk>/delete/',       views.department_delete,    name='department_delete'),

    # Clear data
    path('clear-data/',  views.clear_all_data,  name='clear_all_data'),
    path('delete-data-department/', views.delete_all_data_in_department, name='delete_all_data_in_department'),
]
