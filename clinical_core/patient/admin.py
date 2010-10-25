from django.contrib import admin
from reversion.admin import VersionAdmin
from django.contrib.auth.models import User
from models import *

class PatientAdmin(admin.ModelAdmin):
    list_display=('id', 'doc_id',)
    list_filter = []
admin.site.register(Patient, PatientAdmin)


