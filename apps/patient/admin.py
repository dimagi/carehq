from django.contrib import admin

from django.contrib.auth.models import User
from models import *

class IdentifierTypeAdmin(admin.ModelAdmin):
    list_display=('id', 'description','shortname', 'regex',)
    list_filter = []

admin.site.register(IdentifierType, IdentifierTypeAdmin)

class PatientIdentifierAdmin(admin.ModelAdmin):
    list_display=('id', 'id_type', 'patient', 'id_value',)
    list_filter = ['id_type', 'patient']

admin.site.register(PatientIdentifier, PatientIdentifierAdmin)


class PatientIdentifierInline(admin.StackedInline):
    model = PatientIdentifier    

class PatientAdmin(admin.ModelAdmin):
    list_display=('id', 'user', 'dob', 'is_primary')
    list_filter = []
    inlines = [PatientIdentifierInline]
    
admin.site.register(Patient, PatientAdmin)