from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from datetime import date

class UserProfile(AbstractUser):
    email = models.EmailField(unique=True)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    address = models.CharField(max_length=200)
    date_of_birth = models.DateField(default=date.today)
    contact_no = models.IntegerField(
        validators=[
            MinValueValidator(1500000000),  
            MaxValueValidator(1999999999)
        ], unique=True, default=0000000000
    )
    ACCOUNT_TYPE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    ]
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, blank=False, null=False)
    is_approved = models.BooleanField(default=True)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.username}" 
    
class Department(models.Model):
    DEPARTMENT_CHOICES = [
        ('cardiology', 'Cardiology'),
        ('neurology', 'Neurology'),
        ('orthopedics', 'Orthopedics'),
        ('pediatrics', 'Pediatrics')
    ]

    name = models.CharField(max_length=100, unique=True, choices=DEPARTMENT_CHOICES)
    description = models.TextField()
    head_doctor = models.OneToOneField('DoctorProfile', related_name='head_of_department', unique=True, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.get_name_display()} Department"

class Shift(models.Model):
    SHIFT_CHOICES = [
        ('day', 'Day Shift'),
        ('evening', 'Evening Shift'),
        ('night', 'Night Shift')
    ]

    type = models.CharField(max_length=20, unique=True, choices=SHIFT_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.get_type_display()} - {self.start_time} to {self.end_time}"


class DoctorProfile(models.Model):
    user_profile = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    qualifications = models.TextField()
    
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.user_profile.first_name} {self.user_profile.last_name}"
    

class PatientProfile(models.Model):
    user_profile = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    medical_history = models.TextField()
    prescribed_medications = models.TextField()


    def __str__(self):
        return self.user_profile.username 

    
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
        ('rescheduled', 'Rescheduled'),
        ('pending', 'Pending'),
    ]
    date = models.DateField()
    time = models.TimeField()
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    problem = models.TextField()
    accepted = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Appointment on {self.date} at {self.time} with Dr. {self.doctor} for {self.patient}: {self.get_status_display()}"

class Billing(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('online', 'Online')
    ]

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)

    def __str__(self):
        return f"Billing for {self.patient} - Total Amount: {self.total_amount}, Status: {self.status}"

class Ward(models.Model): 
    WARD_TYPES = [
        ('general', 'General Ward'),
        ('specialized', 'Specialized Ward'),
        ('isolation', 'Isolation Ward'),
        ('hdu', 'High Dependency Unit (HDU)'),
        ('private', 'Private Ward')
    ]

    name = models.CharField(
        max_length=1,
        unique=True,
        validators=[
            RegexValidator(
                regex='^[A-Z]$',  
                message='Ward name should be a single letter from A to Z.',
                code='invalid_ward_name'
            )
        ]
    )
    ward_type = models.CharField(max_length=50,  choices=WARD_TYPES)
    
    @property
    def capacity(self):
        return self.bed_set.count()

    @property
    def occupancy(self):
        return Admission.objects.filter(bed__ward=self).count()

    def __str__(self):
        return f"{self.name} ({self.get_ward_type_display()})"
    
class Bed(models.Model):

    ward = models.ForeignKey(Ward, on_delete=models.CASCADE)
    bed_number = models.IntegerField()
    class Meta:
        unique_together = ('ward', 'bed_number')
    
    @property
    def bed_name(self):
        return f'{self.ward.name}{self.bed_number}'
    def __str__(self):
        return f"{self.ward.name}{self.bed_number}({self.ward.ward_type})"
    
class Admission(models.Model):
    patient = models.OneToOneField(PatientProfile, on_delete=models.CASCADE)
    bed = models.OneToOneField(Bed, on_delete=models.CASCADE)
    admission_datetime = models.DateTimeField()

    def __str__(self):
        return f"Admission for {self.patient} in {self.ward}"
    
class DischargedPatient(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    bed_name = models.CharField(max_length=100)
    admission_datetime = models.DateTimeField()
    discharge_datetime = models.DateTimeField()

    def __str__(self):
        return f"Discharged Patient: {self.patient.user_profile.full_name}"