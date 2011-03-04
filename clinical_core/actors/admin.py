from django.contrib import admin
from models import *


class RoleAdmin(admin.ModelAdmin):
    list_display=('user', 'role_type', 'description')
    list_filter = ['user','role_type']
admin.site.register(Role, RoleAdmin)

class PatientLinkAdmin(admin.ModelAdmin):
    list_display=('patient', 'role','active', 'created_date', 'modified_date')
    list_filter  = ['patient','active']

admin.site.register(PatientLink, PatientLinkAdmin)