from django.contrib import admin
from reversion.admin import VersionAdmin

from django.contrib.auth.models import User
from models import *


try:
    admin.site.unregister(User)
except:
    pass

class UserRevision(VersionAdmin):
    list_display=('id','first_name','last_name','email')

admin.site.register(User, UserRevision)

class CaseProfileAdmin(VersionAdmin):
    list_display = ('user','last_filter','last_login','last_login_from')
admin.site.register(CaseProfile, CaseProfileAdmin)
    
    
class CareTeamAdmin(admin.ModelAdmin):
    list_display=('patient',)
admin.site.register(CareTeam, CareTeamAdmin)

class ProviderRoleAdmin(admin.ModelAdmin):
    list_display=('role',)
admin.site.register(ProviderRole, ProviderRoleAdmin)

class ProviderLinkAdmin(admin.ModelAdmin):
    list_display=('careteam', 'provider','role','notes')
    list_filter =['careteam','provider','role']
admin.site.register(ProviderLink, ProviderLinkAdmin)

class CaregiverLinkAdmin(admin.ModelAdmin):
    list_display=('careteam', 'user','relationship','notes')
    list_filter =['careteam','user','relationship']
admin.site.register(CaregiverLink, CaregiverLinkAdmin)

class CareTeamCaseLinkAdmin(admin.ModelAdmin):
    list_display=('careteam', 'case')
    list_filter =['careteam']
admin.site.register(CareTeamCaseLink, CareTeamCaseLinkAdmin)
    



#class AshandProfileAdmin(VersionAdmin):
#    list_display = ('id','firstname','surname', 'user')
#    list_filter = []    

#admin.site.register(AshandProfile,AshandProfileAdmin)