from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db import IntegrityError
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import UserProfile, PatientProfile, DoctorProfile, Department, Appointment, Admission, Billing, Bed, Ward, Shift, DischargedPatient 
from .forms import DeptShifts,AdminProfileForm, AdmissionForm, DepartmentForm, WardForm, ShiftForm, BedForm, BillingForm, DoctorForm, UserProfileForm, PatientForm, UserFilterForm, PatientFilterForm, DoctorFilterForm, DoctorUserFilterForm, WardFilterForm,  BedFilterForm, BillingFilterForm, DoctorRequestFilterForm, AdmissionFilterForm 


#Home
def home_view(request):
    departments = Department.objects.all()

    head_doctors = {
        department.name: department.head_doctor.user_profile.get_full_name() if department.head_doctor else "No head doctor assigned"
        for department in departments
    }

    patients_count = PatientProfile.objects.count()

    approved_doctors_count = DoctorProfile.objects.filter(user_profile__is_approved=True).count()

    total_beds = Bed.objects.count()

    return render(request, 'home.html', {
        'departments': departments,
        'head_doctors': head_doctors,
        'patients_count': patients_count,
        'approved_doctors_count': approved_doctors_count,
        'total_beds': total_beds,
    })

def department_user_view(request):
    departments = Department.objects.all()
    department_data = []
    for department in departments:
        approved_doctors_count = DoctorProfile.objects.filter(
            department=department, user_profile__is_approved=True
        ).count()
        department_info = {
            'department': department,
            'approved_doctors_count': approved_doctors_count,
        }
        department_data.append(department_info)
    context = {'department_data': department_data}
    return render(request, 'department_user.html', context)

def doctor_user_view(request):
    form = DoctorUserFilterForm(request.GET)
    all_doctors = DoctorProfile.objects.select_related('user_profile').filter(user_profile__is_approved=True)

    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        department = form.cleaned_data.get('department')

        if search_query:
            all_doctors = all_doctors.filter(user_profile__first_name__icontains=search_query) | all_doctors.filter(user_profile__last_name__icontains=search_query)

        if department:
            all_doctors = all_doctors.filter(department = department)

    return render(request, 'doctor_user.html', {'all_doctors': all_doctors, 'form': form})

def signup_view(request):
    error = None
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        email = request.POST.get('email')
        date_of_birth = request.POST.get('dob')
        contact_no = request.POST.get('contact_no')
        account_type = request.POST.get('account_type')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})

        try:
            validate_password(password)
        except ValidationError as e:
            error = ', '.join(e.messages)
            return render(request, 'signup.html', {'error': error})

        try:
            user_profile = UserProfile.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                address=address,
                date_of_birth=date_of_birth,
                contact_no=contact_no,
                account_type=account_type
            )
            
            if user_profile.account_type == 'patient':
                return redirect('patient_signup', user_profile_id=user_profile.id)
            elif user_profile.account_type == 'doctor':
                user_profile.is_approved = False
                user_profile.save()
                return redirect('doctor_signup', user_profile_id=user_profile.id)
            
            return redirect('success')

        except IntegrityError as e:
            error = None
            if 'username' in str(e):
                error = 'Username already exists.'
            elif 'email' in str(e):
                error = 'Email already exists.'
            elif 'contact_no' in str(e):
                error = 'Contact number already exists.' 

    return render(request, 'signup.html', {'error': error})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            
            if user.account_type == 'patient':
                login(request, user)
                return redirect('patient_dashboard')  
                
            elif user.account_type == 'doctor':
                login(request, user)
                return redirect('doctor_dashboard')  
                
            login(request,user)
            return redirect('custom_admin_dashboard')

        messages.error(request, 'Invalid username or password')
        return render(request, 'login.html')
    
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    request.session.flush()
    return redirect('home') 

def cancel_signup(request, user_profile_id):
    user_profile = UserProfile.objects.get(pk=user_profile_id)
    user_profile.delete()
    return redirect('home')

def signup_success_view(request):
    return render(request, 'success.html')


#Admin

@login_required
def custom_admin_dashboard(request):
    total_doctors = UserProfile.objects.filter(account_type='doctor', is_approved=True).count()
    total_patients = UserProfile.objects.filter(account_type='patient').count()
    total_admitted_patients = Admission.objects.count() 
    pending_doctor_requests = UserProfile.objects.filter(account_type='doctor', is_approved=False).count()
    total_billings = Billing.objects.count()
    total_wards = Ward.objects.count()
    total_beds = Bed.objects.count()

    context = {
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_admitted_patients': total_admitted_patients,
        'pending_doctor_requests': pending_doctor_requests,
        'total_billings': total_billings,
        'total_wards': total_wards,
        'total_beds': total_beds,
    }
    
    return render(request, 'custom_admin_dashboard.html', context)

@login_required
def update_admin_profile(request):
    if request.method == 'POST':
        form = AdminProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('custom_admin_dashboard')  
    else:
        form = AdminProfileForm(instance=request.user)
    
    return render(request, 'update_admin_profile.html', {'form': form})


#Admin->UserProfile
@login_required
def view_users(request):
    form = UserFilterForm(request.GET)
    all_users = UserProfile.objects.filter(account_type__in=['patient', 'doctor'], is_approved = True)

    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        gender = form.cleaned_data.get('gender')
        account_type = form.cleaned_data.get('account_type')

        if search_query:
            all_users = all_users.filter(username__icontains=search_query)

        if gender:
            all_users = all_users.filter(gender=gender)

        if account_type:
            all_users = all_users.filter(account_type=account_type)

    all_users = all_users.order_by('username') 

    return render(request, 'view_users.html', {'all_users': all_users, 'form': form})

def create_user(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('view_users')  
    else:
        form = UserProfileForm()
    
    return render(request, 'create_user.html', {'form': form})

def update_user(request, user_id):
    user = get_object_or_404(UserProfile, pk=user_id)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('view_users')
    else:
        form = UserProfileForm(instance=user)
    
    return render(request, 'update_user.html', {'form': form})

def delete_user(request, user_id):
    user = get_object_or_404(UserProfile, pk=user_id)
    
    if request.method == 'POST':
        user.delete()
        return redirect('view_users')  
    
    return render(request, 'delete_confirmation.html', {'user': user})

#Admin -> PatientProfile

@staff_member_required
@login_required
def view_patients(request):
    form = PatientFilterForm(request.GET)
    all_patients = PatientProfile.objects.all()
    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')

        if search_query:
            all_patients = all_patients.filter(user_profile__username__icontains=search_query)
    
    all_patients = all_patients.order_by('user_profile__username')

    return render(request, 'view_patients.html', {'all_patients': all_patients, 'form': form})


@login_required
def create_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient_profile = form.save(commit=False)
            patient_profile.account_type = 'patient'  
            patient_profile.save()
            return redirect('view_patients')  
    else:
        form = PatientForm()
    
    return render(request, 'create_patient.html', {'form': form})

@login_required
def update_patient(request, patient_id):
    patient_profile = get_object_or_404(PatientProfile, pk=patient_id)
    
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient_profile)
        if form.is_valid():
            form.save()
            return redirect('view_patients')  
    else:
        form = PatientForm(instance=patient_profile)
    
    return render(request, 'update_patient.html', {'form': form})

def delete_patient(request, patient_id):
    patient_profile = get_object_or_404(PatientProfile, pk=patient_id)
    
    if request.method == 'POST':
        patient_profile.user_profile.delete()
        return redirect('view_patients')  
    
    return render(request, 'delete_confirmation.html', {'patient_profile': patient_profile})

#Admin -> DoctorProfile

@login_required
def view_doctors(request):
    form = DoctorFilterForm(request.GET)
    all_doctors = DoctorProfile.objects.select_related('user_profile').filter(user_profile__is_approved=True)

    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        department = form.cleaned_data.get('department')

        if search_query:
            all_doctors = all_doctors.filter(user_profile__username__icontains=search_query)

        if department:
            all_doctors = all_doctors.filter(department = department)

    all_doctors = all_doctors.order_by("user_profile__username")

    return render(request, 'view_doctors.html', {'all_doctors': all_doctors, 'form': form})

def create_doctor(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            doctor_profile = form.save(commit=False)
            doctor_profile.account_type = 'doctor'  
            doctor_profile.save()
            return redirect('view_doctors')  
    else:
        form = DoctorForm()
    return render(request, 'create_doctor.html', {'form': form})

def update_doctor(request, doctor_id):
    doctor_profile = get_object_or_404(DoctorProfile, user_profile_id=doctor_id)
    
    if request.method == 'POST':
        form = DoctorForm(request.POST, instance=doctor_profile)
        if form.is_valid():
            form.save()
            return redirect('view_doctors')
    else:
        form = DoctorForm(instance=doctor_profile)
    
    return render(request, 'update_doctor.html', {'form': form})

def delete_doctor(request, doctor_id):
    doctor = get_object_or_404(UserProfile, pk=doctor_id, account_type='doctor')
    
    if request.method == 'POST':
        doctor.delete()
        return redirect('view_doctors')
    
    return render(request, 'delete_confirmation.html', {'doctor': doctor})

@login_required
def doctor_nurse_requests(request):
    form = DoctorRequestFilterForm(request.GET)
    doctor_requests = UserProfile.objects.filter(account_type='doctor', is_approved=False).order_by('-date_joined')
    
    search_query = request.GET.get('search_query')
    if search_query:
        doctor_requests = doctor_requests.filter(username__icontains=search_query)

    doctor_requests = doctor_requests.order_by('-date_joined')

    doctor_details = []
    for doctor_request in doctor_requests:
        doctor_info = {
            'username': doctor_request.username,
            'id': doctor_request.id,
            'first_name': doctor_request.first_name,
            'last_name': doctor_request.last_name,
            'specialization': doctor_request.doctorprofile.specialization,
            'degree': doctor_request.doctorprofile.qualifications,
            'date_joined': doctor_request.date_joined
        }
        doctor_details.append(doctor_info)

    return render(request, 'doctor_nurse_requests.html', {'doctor_details': doctor_details, 'form':form})

@login_required
def approve_account(request, user_id):
    user_profile = UserProfile.objects.get(pk=user_id)
    user_profile.is_approved = True
    user_profile.save()
    return redirect('doctor_nurse_requests')

@login_required
def reject_account(request, user_id):
    user_profile = UserProfile.objects.get(pk=user_id)
    user_profile.delete()
    return redirect('doctor_nurse_requests')

#Admin-> Admission


@login_required
def view_admissions(request):
    form = AdmissionFilterForm(request.GET)
    admissions = Admission.objects.select_related('patient__user_profile')

    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        ward_type = form.cleaned_data.get('ward_type')
        sort_by = form.cleaned_data.get('sort_by')

        if search_query:
            admissions = admissions.filter(
                Q(patient__user_profile__username__icontains=search_query) |
                Q(patient__user_profile__first_name__icontains=search_query) |
                Q(patient__user_profile__last_name__icontains=search_query)
            )

        if ward_type:
            admissions = admissions.filter(bed__ward__ward_type=ward_type)

        if sort_by:
            admissions = admissions.order_by(f'-{sort_by}')

    return render(request, 'view_admissions.html', {'admissions': admissions, 'form': form})


def create_admission(request):
    if request.method == 'POST':
        form = AdmissionForm(request.POST)
        if form.is_valid():
            patient = form.cleaned_data['patient']
            bed = form.cleaned_data['bed']
            admission_datetime = form.cleaned_data['admission_datetime']
            
            admission = Admission.objects.create(
                patient=patient,
                bed=bed,
                admission_datetime=admission_datetime
            )
            return redirect('view_admissions')
    else:
        form = AdmissionForm()
    
    return render(request, 'create_admission.html', {'form': form})

def update_admission(request, admission_id):
    admission = get_object_or_404(Admission, pk=admission_id)
    
    if request.method == 'POST':
        form = AdmissionForm(request.POST, instance=admission)
        if form.is_valid():
            form.save()
            return redirect('view_admissions')  
    else:
        form = AdmissionForm(instance=admission)
    
    return render(request, 'update_admission.html', {'form': form})

def delete_admission(request, admission_id):
    admission = get_object_or_404(Admission, pk=admission_id)
    if request.method == 'POST':
        patient = admission.patient
        billing = Billing.objects.filter(patient=patient).first()
        if billing:
            billing.delete()
        admission.delete()
        return redirect('view_admissions')
    return render(request, 'delete_confirmation.html', {'admission': admission})



#Admin -> DischargedPatient

def view_discharged_patients(request):
    discharged_patients = DischargedPatient.objects.all().order_by('-discharge_datetime')
    return render(request, 'view_discharged_patients.html', {'discharged_patients': discharged_patients})

#Admin->Department

@login_required
def view_departments(request):
    departments = Department.objects.all().order_by("name")

    context = {
        'departments': departments,
    }
    
    return render(request, 'view_departments.html', context)

def create_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('view_departments')
    else:
        form = DepartmentForm()
    return render(request, 'create_department.html', {'form': form})

def update_department(request, department_id):
    department = get_object_or_404(Department, pk=department_id)
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect('view_departments')  
    else:
        form = DepartmentForm(instance=department)
    
    return render(request, 'update_department.html', {'form': form})

def delete_department(request, department_id):
    department = get_object_or_404(Department, pk=department_id)
    if request.method == 'POST':
        department.delete()
        return redirect('view_departments')
    return render(request, 'delete_confirmation.html', {'department': department})

#Admin->Ward

@login_required
def view_wards(request):
    form = WardFilterForm(request.GET)
    wards = Ward.objects.all().order_by('name')

    if form.is_valid():
        name = form.cleaned_data.get('name')
        ward_type = form.cleaned_data.get('ward_type')

        if name:
            wards = wards.filter(name__icontains=name)
        if ward_type:
            wards = wards.filter(ward_type=ward_type)

    context = {
        'wards': wards,
        'form': form,
    }

    return render(request, 'view_wards.html', context)

def create_ward(request):
    if request.method == 'POST':
        form = WardForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('view_wards')  
    else:
        form = WardForm()
    
    return render(request, 'create_ward.html', {'form': form})

def update_ward(request, ward_id):
    ward = get_object_or_404(Ward, pk=ward_id)
    
    if request.method == 'POST':
        form = WardForm(request.POST, instance=ward)
        if form.is_valid():
            form.save()
            return redirect('view_wards') 
    else:
        form = WardForm(instance=ward)
    
    return render(request, 'update_ward.html', {'form': form})

def delete_ward(request, ward_id):
    ward = get_object_or_404(Ward, pk=ward_id)
    if request.method == 'POST':
        ward.delete()
        return redirect('view_wards')
    return render(request, 'delete_confirmation.html', {'ward': ward})

#Admin->Shift

@login_required
def view_shifts(request):
    shifts = Shift.objects.all()
    return render(request, 'view_shifts.html', {'shifts': shifts})

def create_shift(request):
    if request.method == 'POST':
        form = ShiftForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('view_shifts')  
    else:
        form = ShiftForm()
    
    return render(request, 'create_shift.html', {'form': form})

def update_shift(request, shift_id):
    shift = get_object_or_404(Shift, pk=shift_id)
    
    if request.method == 'POST':
        form = ShiftForm(request.POST, instance=shift)
        if form.is_valid():
            form.save()
            return redirect('view_shifts')  
    else:
        form = ShiftForm(instance=shift)
    
    return render(request, 'update_shift.html', {'form': form})

def delete_shift(request, shift_id):
    shift = get_object_or_404(Shift, pk=shift_id)
    if request.method == 'POST':
        shift.delete()
        return redirect('view_shifts')
    return render(request, 'delete_confirmation.html', {'shift': shift})

#Admin->Bed

@login_required
def view_beds(request):
    form = BedFilterForm(request.GET)
    beds = Bed.objects.all().order_by('ward__name')

    ward_id = request.GET.get('ward')
    bed_number = request.GET.get('bed_number')

    if ward_id:
        beds = beds.filter(ward_id=ward_id)
    
    if bed_number:
        beds = beds.filter(bed_number=bed_number)
    
    return render(request, 'view_beds.html', {'form': form, 'beds': beds})

def create_bed(request):
    if request.method == 'POST':
        form = BedForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('view_beds')  
    else:
        form = BedForm()
    
    return render(request, 'create_bed.html', {'form': form})

def update_bed(request, bed_id):
    bed = get_object_or_404(Bed, pk=bed_id)
    
    if request.method == 'POST':
        form = BedForm(request.POST, instance=bed)
        if form.is_valid():
            form.save()
            return redirect('view_beds')  
    else:
        form = BedForm(instance=bed)
    
    return render(request, 'update_bed.html', {'form': form})

def delete_bed(request, bed_id):
    bed = get_object_or_404(Bed, pk=bed_id)
    if request.method == 'POST':
        bed.delete()
        return redirect('view_beds')
    return render(request, 'delete_confirmation.html', {'bed': bed})

#Admin -> Billing
@login_required
def view_billings(request):
    form = BillingFilterForm(request.GET)
    billings = Billing.objects.all().order_by('-date')

    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        date = form.cleaned_data.get('date')
        status = form.cleaned_data.get('status')
        payment_method = form.cleaned_data.get('payment_method')

        if search_query:
            billings = billings.filter(id=search_query)
        if date:
            billings = billings.filter(date=date)
        if status:
            billings = billings.filter(status=status)
        if payment_method:
            billings = billings.filter(payment_method=payment_method)

    return render(request, 'view_billings.html', {'billings': billings, 'form': form})

def create_billing(request):
    if request.method == 'POST':
        form = BillingForm(request.POST)
        if form.is_valid():
            patient_id = form.cleaned_data['patient'].id
            previous_bill = Billing.objects.filter(patient_id=patient_id, status='pending').first()

            if previous_bill:
                messages.error(request, "Patient has a pending billing. Complete the previous billing first.")
                return redirect('create_billing')

            admission = Admission.objects.filter(patient_id=patient_id).first()
            
            if admission:
                billing_instance = form.save(commit=False)
                billing_instance.save()

                if billing_instance.status == 'paid':
                    discharged_patient = DischargedPatient.objects.create(
                        patient=admission.patient,
                        bed_name=admission.bed.bed_name,
                        admission_datetime=admission.admission_datetime,
                        discharge_datetime=billing_instance.date 
                    )
                    admission.delete()

                return redirect('view_billings')
            else:
                messages.error(request, "Patient needs an active admission for billing.")
                return redirect('create_billing')
    else:
        form = BillingForm()
    
    return render(request, 'create_billing.html', {'form': form})


def update_billing(request, billing_id):
    billing = Billing.objects.get(pk=billing_id)
    if request.method == 'POST':
        form = BillingForm(request.POST, instance=billing)
        if form.is_valid():
          
            if form.cleaned_data['status'] == 'paid':
                patient_id = billing.patient.id
                admission = Admission.objects.filter(patient_id=patient_id).first()
                if admission:
                  
                    discharged_patient = DischargedPatient.objects.create(
                        patient=admission.patient,
                        bed_name=admission.bed.bed_name,
                        admission_datetime=admission.admission_datetime,
                        discharge_datetime=timezone.now()  
                    )
                    admission.delete()

            form.save()
            return redirect('view_billings')
    else:
        form = BillingForm(instance=billing)

    return render(request, 'update_billing.html', {'form': form})


def delete_billing(request, billing_id):
    billing = get_object_or_404(Billing, pk=billing_id)
    if request.method == 'POST':
        billing.delete()
        return redirect('view_billings')
    return render(request, 'delete_confirmation.html', {'billing': billing})

@login_required
def patient_dashboard(request):
    user_profile = request.user
    patient_profile = PatientProfile.objects.get(user_profile=user_profile)

    appointments = Appointment.objects.filter(patient=patient_profile)
    medical_history = patient_profile.medical_history
    prescribed_medications = patient_profile.prescribed_medications

    context = {
        'appointments': appointments,
        'medical_history': medical_history,
        'prescribed_medications': prescribed_medications,
    }

    return render(request, 'patient_dashboard.html', context)

def patient_signup_view(request, user_profile_id):
    user_profile = get_object_or_404(UserProfile, pk=user_profile_id)
    if request.method == 'POST':
        medical_history = request.POST.get('medical_history')
        prescribed_medications = request.POST.get('prescriptions')
        user_profile = get_object_or_404(UserProfile, pk=user_profile_id)
        patient_profile = PatientProfile.objects.create(
            user_profile = user_profile,
            medical_history = medical_history,
            prescribed_medications = prescribed_medications
        )
        patient_profile.save()
        return redirect('success')
    return render(request, 'patient_signup.html', {'user_profile': user_profile})

@login_required
def patient_dashboard(request):

    user_profile = request.user
    patient_profile = PatientProfile.objects.get(user_profile=user_profile)
    appointments = Appointment.objects.filter(patient=patient_profile)
    admission = Admission.objects.get(patient=patient_profile)
    paymentStatus = Billing.objects.get(patient=patient_profile)
    medical_history = patient_profile.medical_history
    prescribed_medications = patient_profile.prescribed_medications


    search_query = request.GET.get('search_query', '')
    doctors = UserProfile.objects.filter(
        Q(first_name__icontains=search_query) |
        Q(last_name__icontains=search_query),
        account_type='doctor'
    )


    sort_order = request.GET.get('sort', '')
    if sort_order == 'asc':
        doctors = doctors.order_by('first_name')
    elif sort_order == 'desc':
        doctors = doctors.order_by('-first_name')


    context = {
        'appointments': appointments,
        'medical_history': medical_history,
        'prescribed_medications': prescribed_medications,
        'doctors': doctors,
        'admission': admission,
        'paymentStatus': paymentStatus,
    }


    return render(request, 'patient_dashboard.html', context)


def update_profile(request):

    if request.method == 'POST':

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        mail = request.POST.get('mail')
        contacts = request.POST.get('con')
        user_profile = request.user
        user_profile.first_name = first_name
        user_profile.last_name = last_name
        user_profile.address = address
        user_profile.email = mail
        user_profile.contact_no = contacts
        user_profile.address = address
        user_profile.save()
        user_profile = request.user

        patient_profile = PatientProfile.objects.get(user_profile=user_profile)
        appointments = Appointment.objects.filter(patient=patient_profile)
        admission = Admission.objects.get(patient=patient_profile)
        paymentStatus = Billing.objects.get(patient=patient_profile)
        medical_history = patient_profile.medical_history
        prescribed_medications = patient_profile.prescribed_medications

        search_query = request.GET.get('search_query', '')
        doctors = UserProfile.objects.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query),
            account_type='doctor'
        )

        sort_order = request.GET.get('sort', '')
        if sort_order == 'asc':
            doctors = doctors.order_by('first_name')
        elif sort_order == 'desc':
            doctors = doctors.order_by('-first_name')

        context = {
            'appointments': appointments,
            'medical_history': medical_history,
            'prescribed_medications': prescribed_medications,
            'doctors': doctors,
            'admission': admission,
            'paymentStatus': paymentStatus,
        }

        return render(request, 'patient_dashboard.html', context)

def appointment_view(request, doctorID):
    if request.method == 'POST':
       
        patient_id = request.POST.get('patient')
        date = request.POST.get('date')
        time = request.POST.get('time')
        problem = request.POST.get('problem')
        status = request.POST.get('status')

        if not patient_id:
            return HttpResponse("Invalid patient ID")
        try:
            patient_id = int(patient_id)
            doctor_id = int(doctorID)  
        except ValueError:
            return HttpResponse("Invalid patient or doctor ID")
        patient = get_object_or_404(PatientProfile, id=patient_id)
        doctor = get_object_or_404(DoctorProfile, id=doctor_id)
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date=date,
            time=time,
            problem=problem,
            status="Scheduled"
        )
        appointment.save()
        return redirect('success')
    return render(request, 'appointment.html', {'doctorId': doctorID})


@login_required
def doctor_dashboard(request):
    user_profile = request.user
    if user_profile.is_approved:
        doctor = DoctorProfile.objects.get(user_profile=user_profile)
        appointments = Appointment.objects.filter(doctor=doctor)
        patient_appointments = Appointment.objects.filter(doctor=doctor).values_list('patient', flat=True)

        return render(request, 'doctor_dashboard.html', {
            'doctor': doctor,
            'appointments': appointments,
            'patient_appointments': patient_appointments
        })
    else:
        messages.error(request, 'Your doctor account has not been approved yet.')
        return redirect('login')

def appointment_list(request):
    appointments = Appointment.objects.all()
    return render(request, 'appointment_list.html', {'appointments': appointments})

def accept_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.accepted = True
    appointment.save()
    return redirect('appointment_list')


def doctor_signup_view(request, user_profile_id):
    form = DeptShifts()
    user_profile = get_object_or_404(UserProfile, pk=user_profile_id)
    if request.method == 'POST':
        form = DeptShifts(request.POST)
        if form.is_valid():
            department = form.cleaned_data['department']
            shift = form.cleaned_data['shift']
            specialization = request.POST.get('specialization')
            degree = request.POST.get('degree') 
            user_profile = get_object_or_404(UserProfile, pk=user_profile_id)
            doctor_profile = DoctorProfile.objects.create(
                user_profile = user_profile,
                qualifications = degree,
                specialization = specialization,
                department = department,
                shift = shift
            )
            doctor_profile.save()
            return redirect('success')
    return render(request, 'doctor_signup.html', {'form': form, 'user_profile': user_profile})




