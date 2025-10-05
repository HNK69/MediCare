from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone", "age", "gender", "blood_group")
    search_fields = ("user__username", "user__email", "phone")


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "specialization", "qualification", "experience_years", "license_number")
    search_fields = ("user__username", "specialization", "license_number")

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "doctor", "date", "time", "status")  
    list_filter = ("status", "date", "doctor")
    search_fields = ("patient__user__username", "doctor__user__username")
