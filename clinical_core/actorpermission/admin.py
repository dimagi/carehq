from django.contrib import admin
from actorpermission.models.clinicaluser import ClinicalUserProfile

class ClinicalUserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_doc_id','profiles',)
    list_filter = []
admin.site.register(ClinicalUserProfile, ClinicalUserProfileAdmin)