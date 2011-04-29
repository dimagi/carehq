from django.contrib import admin
from actors.models import *


class RoleAdmin(admin.ModelAdmin):
    list_display=('user', 'role_type', 'description')
    list_filter = ['user','role_type']
admin.site.register(Role, RoleAdmin)

class PatientLinkAdmin(admin.ModelAdmin):
    list_display=('patient', 'role','active', 'created_date', 'modified_date')
    list_filter  = ['patient','active']

admin.site.register(PatientLink, PatientLinkAdmin)


class ClinicalUserProfileAdmin(admin.ModelAdmin):
    list_display=('user', 'profile_doc_id', 'couchdoc')

admin.site.register(ClinicalUserProfile, ClinicalUserProfileAdmin)