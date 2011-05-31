from .models.actorprofilemodels import ClinicalUserProfile
from django.contrib import admin

class ClinicalUserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_doc_id','profiles',)
    list_filter = []
admin.site.register(ClinicalUserProfile, ClinicalUserProfileAdmin)