from django.contrib import admin
from models import *

class PatientAdmin(admin.ModelAdmin):
    list_display=('id', 'doc_id', 'full_name',)
    list_filter = []
admin.site.register(Patient, PatientAdmin)



