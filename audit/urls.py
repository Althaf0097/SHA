from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('audit/new/', views.audit_form, name='audit_form'),
    path('audit/<int:audit_id>/patient/', views.add_patient, name='add_patient'),
    path('audit/records/', views.view_records, name='view_records'),
    path('audit/report/', views.report, name='report'),
    path('audit/download/', views.download_all_data, name='download_all_data'),
    
    # Hospital Records URLs
    path('audit/hospitals/', views.hospital_records, name='hospital_records'),
    path('audit/hospitals/<str:hospital_id>/patients/', views.hospital_patients, name='hospital_patients'),
    path('audit/hospitals/<str:hospital_id>/create/', views.create_hospital, name='create_hospital'),
    path('audit/hospitals/<str:hospital_id>/', views.get_hospital, name='get_hospital'),
    path('audit/hospitals/<str:hospital_id>/edit/', views.edit_hospital, name='edit_hospital'),
    path('audit/hospitals/<str:hospital_id>/delete/', views.delete_hospital, name='delete_hospital'),
    path('audit/hospital/<str:hospital_id>/patients/download/', views.download_patient_data, name='download_patient_data'),
    path('audit/hospital/<str:hospital_id>/download-excel/', views.download_patient_excel, name='download_patient_excel'),
    
    # Patient CRUD URLs
    path('audit/patient/<int:patient_id>/', views.get_patient, name='get_patient'),
    path('audit/patient/<int:patient_id>/edit/', views.edit_patient, name='edit_patient'),
    path('audit/patient/<int:patient_id>/delete/', views.delete_patient, name='delete_patient'),
    
    # Admin Panel URLs
    path('admin/', views.admin_panel, name='admin_panel'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/district/add/', views.add_district, name='add_district'),
    path('admin/district/<int:district_id>/edit/', views.edit_district, name='edit_district'),
    path('admin/district/<int:district_id>/delete/', views.delete_district, name='delete_district'),
    path('admin/user/add/', views.add_user, name='add_user'),
    path('admin/user/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('admin/user/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('admin/statistics/', views.audit_statistics, name='audit_statistics'),
]
