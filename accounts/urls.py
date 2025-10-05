from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Authentication
    path("login/", views.LoginPage, name="login"),
    path("register/", views.RegisterPage, name="register"),
    path("logout/", views.logoutUser, name="logout"),

    path('api/call_gemini/', views.call_gemini_api, name='call_gemini_api'),

    # Dashboards
    path("dashboard/patient/", views.patient_dashboard, name="patient_dashboard"),
    path("dashboard/doctor/", views.doctor_dashboard, name="doctor_dashboard"),

    # Doctor routes
    path("appointments/<int:appointment_id>/status/<str:status>/", views.update_appointment_status, name="update_appointment_status"),
    path("doctor/appointments/", views.appointments_list, name="appointments_list"),
    path("patients/", views.patients_list, name="patients_list"),
    path("doctor/appointments/<int:appointment_id>/", views.doctor_patient_appointment_detail, name="doctor_patient_appointment_detail"),
    path("doctor_profile/", views.doctor_profile, name="doctor_profile"),

    # Patient routes
    path("appointments/<int:appointment_id>/", views.appointment_detail, name="appointment_detail"),
    path("appointments/<int:appointment_id>/cancel/", views.appointment_cancel, name="appointment_cancel"),
    path("appointments/clear/", views.clear_past_appointments, name="clear_past_appointments"),
    path("patient_appointments/", views.patient_appointments, name="patient_appointments"),
    path("patient_profile/", views.patient_profile, name="patient_profile"),
    path("book_appointment/", views.book_appointment, name="book_appointment"),

    # Password reset system
    path('password_reset/',
         auth_views.PasswordResetView.as_view(template_name="registration/password_reset.html"),
         name='password_reset'),

    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"),
         name='password_reset_complete'),
]
