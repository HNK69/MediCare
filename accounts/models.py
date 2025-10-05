from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Patient(models.Model):
    user = models.OneToOneField(User,null=True,on_delete=models.CASCADE)
    phone = models.CharField(max_length=200,null=True)
    address = models.TextField(null=True,blank=True)
    age = models.IntegerField(null=True)
    gender = models.CharField(max_length=10,choices=[('Male','Male'),('Female','Female'),('Other','Other')],null=True)
    blood_group = models.CharField(max_length=200,null=True)

    def __str__(self):
        return self.user.username
    
class Doctor(models.Model):
    user = models.OneToOneField(User,null=True,on_delete=models.CASCADE)
    specialization = models.CharField(max_length=20,null=True)
    phone = models.CharField(max_length=20,null=True,blank=True,unique=True) 
    experience_years = models.IntegerField(null=True)
    qualification = models.CharField(max_length=100,null=True,blank=True)
    license_number = models.CharField(max_length=50, unique=True, null=True, blank=True)


    def __str__(self):
        return f"Dr. {self.user.username} ({self.specialization})"
    

class Appointment(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="appointments"   # ✅ clean reverse relation
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="appointments"   # ✅ clean reverse relation
    )
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Confirmed', 'Confirmed'),
            ('Cancelled', 'Cancelled'),
            ('Completed', 'Completed')
        ],
        default='Pending'
    )
    reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.patient.user.username} → Dr. {self.doctor.user.username} on {self.date}"


class Prescription(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    prescribed_by = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    details = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.appointment.patient.user.username} on {self.date}"


class Bill(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[('Unpaid', 'Unpaid'), ('Paid', 'Paid')],
        default='Unpaid'
    )
    date_issued = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Bill {self.id} for {self.appointment.patient.user.username}"


class Report(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    report_file = models.FileField(upload_to="reports/")
    description = models.TextField(blank=True, null=True)
    date_uploaded = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.appointment.patient.user.username} uploaded on {self.date_uploaded}"

