from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile, DischargedPatient, DoctorProfile, PatientProfile, Admission, Appointment, Bed, Billing, Department, Shift, Ward

class UserAdmin(BaseUserAdmin):
    pass

admin.site.register(UserProfile, UserAdmin)
admin.site.register(DoctorProfile)
admin.site.register(DischargedPatient) 
admin.site.register(PatientProfile)
admin.site.register(Admission)
admin.site.register(Appointment)
admin.site.register(Bed)
admin.site.register(Billing)
admin.site.register(Department)
admin.site.register(Shift)
admin.site.register(Ward)
