from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *

class CreateUserForm(UserCreationForm):
    ROLE_CHOICES = [
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)
    license_number = forms.CharField(
        required=False,
        max_length=50,
        help_text="Required if registering as a doctor."
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role', 'license_number']




class EmailOrUsernameAuthenticationForm(forms.Form):
    username = forms.CharField(label="Username or Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)



class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ["specialization", "phone", "experience_years", "qualification", "license_number"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make license_number read-only in form
        self.fields["license_number"].disabled = True



from django import forms
from .models import Patient

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['phone', 'address', 'age', 'gender', 'blood_group']

    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)
        
        # Common CSS classes for form inputs
        base_classes = "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-200"
        
        # Applying classes and placeholders to each field
        self.fields['phone'].widget.attrs.update({
            'class': base_classes,
            'placeholder': 'e.g., +91 98765 43210'
        })
        self.fields['address'].widget.attrs.update({
            'class': base_classes + " h-24", # Taller for textarea
            'placeholder': 'Enter your full address'
        })
        self.fields['age'].widget.attrs.update({
            'class': base_classes,
            'placeholder': 'e.g., 25'
        })
        self.fields['gender'].widget.attrs.update({
            'class': base_classes
        })
        self.fields['blood_group'].widget.attrs.update({
            'class': base_classes,
            'placeholder': 'e.g., O+'
        })

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={
                'placeholder': 'Describe your symptoms or reason for appointment',
                'class': 'form-control'}),
            'status': forms.HiddenInput(),  # optional: hide status, default 'Pending'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional: only allow selecting active doctors
        self.fields['doctor'].queryset = Doctor.objects.all()
        # self.fields['status'].initial = 'Pending'




