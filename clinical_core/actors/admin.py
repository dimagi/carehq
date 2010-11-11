from django.contrib import admin
from models import *

class ActorAdmin(admin.ModelAdmin):
    list_display=('title', 'user')
    list_filter = ['role']
admin.site.register(Actor, ActorAdmin)


class RoleAdmin(admin.ModelAdmin):
    list_display=('user', 'role_type', 'description')
    list_filter = ['user','role_type']
admin.site.register(Role, RoleAdmin)

class PatientActorLinkAdmin(admin.ModelAdmin):
    list_display=('patient', 'actor','active', 'created_date', 'modified_date')
    list_filter  = ['patient','active']

admin.site.register(PatientActorLink, PatientActorLinkAdmin)