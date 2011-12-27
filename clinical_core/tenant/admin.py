from django.contrib import admin
from models import *

class TenantAdmin(admin.ModelAdmin):
    list_display=('prefix', 'name', 'full_name', 'is_active')
    list_filter = ['is_active']
admin.site.register(Tenant, TenantAdmin)

class TenantActorAdmin(admin.ModelAdmin):
    list_display=('tenant', 'actor',)
    list_filter = ['tenant']
admin.site.register(TenantActor, TenantActorAdmin)
