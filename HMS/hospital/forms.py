from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import UserProfile, Department, Shift, Admission, Ward, Bed, PatientProfile, Billing, DoctorProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['username', 'first_name', 'last_name', 'email', 'gender', 'address', 'date_of_birth', 'contact_no', 'account_type', 'is_approved']

class AdminProfileForm(UserChangeForm):
    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES)
    address = forms.CharField(max_length=200)
    date_of_birth = forms.DateField()
    contact_no = forms.IntegerField(
        validators=[
            MinValueValidator(1500000000),  
            MaxValueValidator(1999999999)
        ]
    ) 

    class Meta:
        model = UserProfile
        fields = ['username', 'first_name', 'last_name', 'email', 'gender', 'address', 'date_of_birth', 'contact_no']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['account_type'] = 'admin'
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.account_type = 'admin'
        if commit:
            instance.save()
        return instance

class UserFilterForm(forms.Form):
    GENDER_CHOICES = [('', '---------')] + UserProfile.GENDER_CHOICES
    ACCOUNT_TYPE_CHOICES = [('', '---------')] + UserProfile.ACCOUNT_TYPE_CHOICES

    search_query = forms.CharField(label='Search by Username', required=False)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False, initial='')
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE_CHOICES, required=False, initial='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gender'].initial = ''  
        self.fields['account_type'].initial = ''

class PatientFilterForm(forms.Form):
    search_query = forms.CharField(label='Search by Username', required=False)

class DoctorFilterForm(forms.Form):
    search_query = forms.CharField(label='Search by Username',required=False)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False, empty_label='Select department')

class DoctorUserFilterForm(forms.Form):
    search_query = forms.CharField(label='Search by Name',required=False)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False, empty_label='Select department')

class WardFilterForm(forms.Form):
    WARD_CHOICES = [('', '---------')] + list(Ward.WARD_TYPES)

    ward_type = forms.ChoiceField(choices=WARD_CHOICES, required=False, label='Ward Type', initial='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ward_type'].initial = ''  


class BedFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ward_choices = [('', '---------')] + [(ward.id, ward) for ward in Ward.objects.all()]
        self.fields['ward'] = forms.ChoiceField(choices=ward_choices, required=False, label='Ward')

    bed_number = forms.IntegerField(required=False, label='Bed Number')

class BillingFilterForm(forms.Form):
    search_query = forms.IntegerField(label='Search by Billing ID',required=False )
    date = forms.DateField(required=False, label='Date')
    STATUS_CHOICES = [('', '---------')] + Billing.STATUS_CHOICES
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, label='Status')
    PAYMENT_METHOD_CHOICES = [('', '---------')] + Billing.PAYMENT_METHOD_CHOICES
    payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES, required=False, label='Payment Method')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        self.fields['status'].initial = ''

class AdmissionFilterForm(forms.Form):
    search_query = forms.CharField(label='Search by Username or Name', required=False)
    WARD_TYPES = [('', '---------')] + Ward.WARD_TYPES
    ward_type = forms.ChoiceField(choices=WARD_TYPES, required=False, label='Ward Type')
    sort_by = forms.ChoiceField(
        label='Sort by',
        choices=(
            ('', 'Select'),
            ('admission_datetime', 'Admission Date'),
        ),
        required=False
    )

class DoctorRequestFilterForm(forms.Form):
    search_query = forms.CharField(label='Search by Username', required=False)

class DeptShifts(forms.Form):
    department = forms.ModelChoiceField(queryset=Department.objects.all())
    shift = forms.ModelChoiceField(queryset=Shift.objects.all())

class AdmissionForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = ['patient', 'bed', 'admission_datetime'] 
        widgets = {
            'admission_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description', 'head_doctor']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['head_doctor'].queryset = DoctorProfile.objects.filter(
            user_profile__is_approved=True,
            user_profile__account_type='doctor'
        )

class WardForm(forms.ModelForm):
    class Meta:
        model = Ward
        fields = ['name', 'ward_type']

class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ['type', 'start_time', 'end_time']

class BedForm(forms.ModelForm):
    class Meta:
        model = Bed
        fields = ['ward', 'bed_number'] 
        
class BillingForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = ['patient', 'total_amount', 'date', 'status', 'payment_method']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class DoctorForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['user_profile', 'department', 'shift', 'specialization', 'qualifications'] 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_profile'].queryset = UserProfile.objects.filter(
            is_approved=True,
            account_type='doctor'
        )
class PatientForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ['user_profile', 'medical_history', 'prescribed_medications']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_profile'].queryset = UserProfile.objects.filter(
            is_approved=True,
            account_type='patient'
        )

