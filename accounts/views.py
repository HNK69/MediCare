from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import * # Add this import if you have a custom form, otherwise use UserCreationForm directly
from django.forms import inlineformset_factory
from django.contrib.auth import authenticate,login,logout 
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import date, time
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.utils import timezone
from .models import Appointment, Prescription, Bill, Report, Doctor
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

# Create your views here.

def home(request):
    return render(request, "accounts/landing.html")  # template file path

from django.shortcuts import render
from django.conf import settings

# def home(request):
#     return render(request, "accounts/landing.html", {
#         "GOOGLE_API_KEY": settings.GEMINI_API_KEY  # from settings.py / .env
#     })



def RegisterPage(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        role = request.POST.get('role')
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            group = Group.objects.get(name=role)
            user.groups.add(group)

            if role == 'patient':
                Patient.objects.create(user=user)
            elif role == 'doctor':
                license_number = form.cleaned_data.get('license_number')
                Doctor.objects.create(user=user, license_number=license_number)

            messages.success(request, f"Account created successfully {username}! Please login.")
            return redirect('login')
    else:
        form = CreateUserForm()

    context = {'form': form}
    return render(request, 'accounts/register.html', context)





def LoginPage(request):
    if request.method == 'POST':
        form = EmailOrUsernameAuthenticationForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember = request.POST.get('remember')  # <-- get checkbox value

            # Try username login
            user = authenticate(request, username=username_or_email, password=password)

            # If username login fails, try email
            if user is None:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None

            if user is not None:
                login(request, user)

                # ✅ handle "remember me"
                if remember:
                    request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days
                else:
                    request.session.set_expiry(0)  # expire when browser closes

                # Redirect based on group
                if user.groups.filter(name='doctor').exists():
                    return redirect('doctor_dashboard')
                elif user.groups.filter(name='patient').exists():
                    return redirect('patient_dashboard')
                else:
                    messages.warning(request, "Your account doesn't have a role assigned.")
                    return redirect('login')
            else:
                messages.error(request, "Invalid username or password")
    else:
        form = EmailOrUsernameAuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})






# accounts/views.py
@login_required
def doctor_dashboard(request):
    doctor = get_object_or_404(Doctor, user=request.user)

    # All appointments for this doctor
    appointments = Appointment.objects.filter(doctor=doctor).order_by("-date", "-time")

    # Recent patients (last 5 unique patients with appointments to this doctor)
    recent_patients = Patient.objects.filter(appointments__doctor=doctor).distinct()[:5]

    context = {
        "doctor": doctor,
        "appointments": appointments,
        "recent_patients": recent_patients,
        "total_patients": Patient.objects.filter(appointments__doctor=doctor).distinct().count(),
    }
    return render(request, "accounts/doctor_dashboard.html", context)



def update_appointment_status(request, appointment_id, status):
    doctor = get_object_or_404(Doctor, user=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)

    if status in ["Confirmed", "Cancelled", "Completed"]:
        appointment.status = status
        appointment.save()
        messages.success(request, f"Appointment marked as {status}.")
    else:
        messages.error(request, "Invalid status update.")

    return redirect("doctor_dashboard")



def logoutUser(request):
    logout(request)
    return redirect('login')





@login_required
def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient__user=request.user)
    return render(request, 'accounts/appointment_detail.html', {"appointment": appointment})



@login_required
def appointment_cancel(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient__user=request.user)

    if request.method == "POST":
        # User confirmed cancellation
        appointment.status = "Cancelled"
        appointment.save()
        messages.success(request, "Your appointment has been cancelled.")
        return redirect("patient_dashboard")

    # If GET → show confirmation page
    return render(request, "accounts/appointment_cancel_confirm.html", {"appointment": appointment})

@login_required
def doctor_profile(request):
    doctor = get_object_or_404(Doctor, user=request.user)

    if request.method == "POST":
        form = DoctorForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("doctor_dashboard")
    else:
        form = DoctorForm(instance=doctor)

    return render(request, "accounts/doctor_profile.html", {"form": form, "doctor": doctor})





@login_required
def patient_profile(request):
    try:
        patient = request.user.patient  # Get linked Patient if exists
    except Patient.DoesNotExist:
        patient = None

    if request.method == "POST":
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.user = request.user
            patient.save()
            return redirect("patient_dashboard")  # reload profile after save
    else:
        form = PatientForm(instance=patient)

    return render(request, "accounts/profile.html", {"form": form})


@login_required
def patient_dashboard(request):
    patient = Patient.objects.get(user=request.user)

    upcoming_appointments = Appointment.objects.filter(
        patient=patient
    ).order_by("date", "time")

    context = {
        "patient": patient,
        "upcoming_appointments": upcoming_appointments,
        "upcoming_appointments_count": upcoming_appointments.count(),
        "past_appointments_count": Appointment.objects.filter(patient=patient, date__lt=timezone.now().date()).count(),
        "doctors": Doctor.objects.all(),
    }
    return render(request, "accounts/patient_dashboard.html", context)


@login_required
def book_appointment(request):
    # Get logged in patient
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect("home")  # Or error page
    
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient   # link to logged-in patient
            appointment.status = "Pending"  # default
            appointment.save()
            return redirect("patient_dashboard")  # redirect after booking
    else:
        form = AppointmentForm()

    doctors = Doctor.objects.all()
    context = {
        'form': form,
        'doctors': doctors   # ✅ lowercase name
    }
    return render(request, 'accounts/book_appointment.html', context)

from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Appointment, Patient

@login_required
def patient_appointments(request):
    patient = get_object_or_404(Patient, user=request.user)
    today = date.today()

    upcoming_appointments = Appointment.objects.filter(
        patient=patient,
        date__gte=today,
        status__in=["Pending", "Confirmed"]
    )

    past_appointments = Appointment.objects.filter(
        patient=patient
    ).exclude(
        id__in=upcoming_appointments.values_list("id", flat=True)
    )

    return render(request, "accounts/patient_appointments.html", {
        "upcoming_appointments": upcoming_appointments,
        "past_appointments": past_appointments
    })


@login_required
def clear_past_appointments(request):
    patient = get_object_or_404(Patient, user=request.user)
    today = date.today()

    if request.method == "POST":
        from django.db.models import Q
        deleted, _ = Appointment.objects.filter(
            patient=patient
        ).filter(
            Q(date__lt=today) | Q(status="Cancelled")
        ).delete()

        if deleted:
            messages.success(request, f"{deleted} past appointments cleared.")
        else:
            messages.info(request, "No past appointments to clear.")

        # ✅ redirect will force a new query in patient_appointments view
        return redirect("patient_appointments")

    return HttpResponse("Invalid request", status=400)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Appointment, Doctor
from django.contrib import messages

@login_required
def appointments_list(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor).order_by("date", "time")
    return render(request, "accounts/appointments_list.html", {"appointments": appointments})

from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Appointment, Patient, Doctor

@login_required
def patients_list(request):
    # Get logged-in doctor
    doctor = get_object_or_404(Doctor, user=request.user)

    # Get unique patients who have appointments with this doctor
    patients = Patient.objects.filter(
        appointments__doctor=doctor
    ).distinct()

    context = {
        "patients": patients
    }
    return render(request, "accounts/patients_list.html", context)


@login_required
def update_appointment_status(request, appointment_id, status):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if not request.user.groups.filter(name="doctor").exists():
        messages.error(request, "You are not allowed to update appointments.")
        return redirect("doctor_dashboard")

    if request.method == "POST":
        if status in ["Pending", "Confirmed", "Completed", "Cancelled"]:
            appointment.status = status
            appointment.save()
            messages.success(request, f"Appointment marked as {status}.")
        else:
            messages.error(request, "Invalid status.")
    return redirect("doctor_dashboard")




@login_required
def doctor_patient_appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Optional: Ensure only doctors can view this page
    if not request.user.groups.filter(name="doctor").exists():
        messages.error(request, "You do not have permission to view this page.")
        return redirect("doctor_dashboard")

    context = {"appointment": appointment}
    return render(request, "accounts/doctor_patient_appointment_detail.html", context)

import json
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

@require_POST
def call_gemini_api(request):
    """
    This view acts as a secure proxy to the Google Gemini API.
    It receives a request from the frontend, adds the secret API key,
    forwards the request to Google, and then sends Google's response
    back to the frontend.
    """
    try:
        # 1. Get the data from the frontend's request
        data = json.loads(request.body)
        user_query = data.get('user_query')
        system_prompt = data.get('system_prompt')
        use_grounding = data.get('use_grounding', False)

        if not user_query or not system_prompt:
            return JsonResponse({'error': 'Missing user_query or system_prompt'}, status=400)

        # 2. Get the secret API key from Django settings
        api_key = settings.GOOGLE_API_KEY
        if not api_key:
            return JsonResponse({'error': 'GOOGLE_API_KEY not configured in Django settings.'}, status=500)
        
        gemini_api_url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={api_key}'

        # 3. Construct the payload for the Google Gemini API
        payload = {
            "contents": [{"parts": [{"text": user_query}]}],
            "systemInstruction": {"parts": [{"text": system_prompt}]},
        }

        if use_grounding:
            payload["tools"] = [{"google_search": {}}]

        # 4. Make the server-to-server request to Google
        response = requests.post(gemini_api_url, json=payload, headers={'Content-Type': 'application/json'})
        
        # Raise an exception if the call to Google failed
        response.raise_for_status() 

        google_response_data = response.json()

        # 5. Extract the relevant data to send back to the frontend
        candidate = google_response_data.get('candidates', [{}])[0]
        content = candidate.get('content', {}).get('parts', [{}])[0]
        text = content.get('text', '')

        if not text:
             return JsonResponse({'error': 'Received an empty response from the AI.'}, status=500)

        final_response = {'text': text}

        if use_grounding:
            grounding_metadata = candidate.get('groundingMetadata', {})
            attributions = grounding_metadata.get('groundingAttributions', [])
            sources = [
                {'uri': attr.get('web', {}).get('uri'), 'title': attr.get('web', {}).get('title')}
                for attr in attributions if attr.get('web', {}).get('uri')
            ]
            final_response['sources'] = sources

        return JsonResponse(final_response)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except requests.exceptions.RequestException as e:
        # This will catch network errors or non-200 responses from Google
        return JsonResponse({'error': f'Failed to call Google API: {e}'}, status=502) # Bad Gateway
    except Exception as e:
        # Catch any other unexpected errors
        return JsonResponse({'error': f'An unexpected server error occurred: {e}'}, status=500)
