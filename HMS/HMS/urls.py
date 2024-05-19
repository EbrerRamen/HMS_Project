"""
URL configuration for HMS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from hospital import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('department_user_view/', views.department_user_view, name='department_user_view'),
    path('doctor_user_view/', views.doctor_user_view, name='doctor_user_view'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('cancel/signup/<int:user_profile_id>/', views.cancel_signup, name='cancel_signup'),
    path('success/', views.signup_success_view, name='success'),
    path('logout/', views.user_logout, name='logout'),

    #Admin
    path('custom_admin_dashboard/', views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('edit-admin-profile/', views.update_admin_profile, name='edit_admin_profile'), 

    path('custom_admin_dashboard/create_admission/', views.create_admission, name='create_admission'),
    path('view_admissions/', views.view_admissions, name='view_admissions'),
    path('admissions/<int:admission_id>/edit/', views.update_admission, name='edit_admission'),
    path('admissions/<int:admission_id>/delete/', views.delete_admission, name='delete_admission'),
    path('discharged_patients/', views.view_discharged_patients, name='view_discharged_patients'),

    path('create_department/', views.create_department, name='create_department'),
    path('view_departments/', views.view_departments, name='view_departments'),
    path('departments/<int:department_id>/edit/', views.update_department, name='edit_department'),
    path('departments/<int:department_id>/delete/', views.delete_department, name='delete_department'),

    path('ward/create/', views.create_ward, name='create_ward'),
    path('ward/list/', views.view_wards, name='view_wards'),
    path('wards/<int:ward_id>/edit/', views.update_ward, name='edit_ward'),
    path('wards/<int:ward_id>/delete/', views.delete_ward, name='delete_ward'),

    path('shifts/create/', views.create_shift, name='create_shift'),
    path('shift/list/', views.view_shifts, name='view_shifts'),
    path('shifts/<int:shift_id>/edit/', views.update_shift, name='edit_shift'),
    path('shifts/<int:shift_id>/delete/', views.delete_shift, name='delete_shift'),
    
    path('create_billing/', views.create_billing, name='create_billing'),
    path('view_billings/', views.view_billings, name='view_billings'),
    path('billings/<int:billing_id>/delete/', views.delete_billing, name='delete_billing'),
    path('billings/<int:billing_id>/edit/', views.update_billing, name='edit_billing'),
    
    path('create_bed/', views.create_bed, name='create_bed'),
    path('beds/', views.view_beds, name='view_beds'),
    path('beds/<int:bed_id>/edit/', views.update_bed, name='edit_bed'),
    path('beds/<int:bed_id>/delete/', views.delete_bed, name='delete_bed'),
    
    path('view-patients/', views.view_patients, name='view_patients'),
    path('create-patient/', views.create_patient, name='create_patient'),
    path('edit-patient/<int:patient_id>/', views.update_patient, name='edit_patient'),
    path('delete-patient/<int:patient_id>/', views.delete_patient, name='delete_patient'),
    
    path('create_doctor/', views.create_doctor, name='create_doctor'),
    path('view_doctors/', views.view_doctors, name='view_doctors'),
    path('edit-doctor/<int:doctor_id>/', views.update_doctor, name='edit_doctor'),
    path('delete-doctor/<int:doctor_id>/', views.delete_doctor, name='delete_doctor'),

    path('create_user/', views.create_user, name='create_user'),
    path('view_users/', views.view_users, name='view_users'),
    path('edit_user/<int:user_id>/', views.update_user, name='edit_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),

    path('doctor-nurse-requests/', views.doctor_nurse_requests, name='doctor_nurse_requests'),
    path('approve-account/<int:user_id>/', views.approve_account, name='approve_account'),
    path('reject-account/<int:user_id>/', views.reject_account, name='reject_account'),
    
    #PatientProfile
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('patient_signup/<int:user_profile_id>/', views.patient_signup_view, name='patient_signup'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('appointment_view/<int:doctorID>/', views.appointment_view, name='appointment_view'),

    #DoctorProfile
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor_signup/<int:user_profile_id>/', views.doctor_signup_view, name='doctor_signup'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/accept/<int:appointment_id>/', views.accept_appointment, name='accept_appointment'),
]   