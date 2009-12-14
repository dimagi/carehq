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
    

#class AshandProfileAdmin(VersionAdmin):
#    list_display = ('id','firstname','surname', 'user')
#    list_filter = []    

#admin.site.register(AshandProfile,AshandProfileAdmin)