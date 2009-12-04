from django.contrib import admin
from reversion.admin import VersionAdmin
from django.contrib.auth.models import User

from models import CaseAction, Category, Priority, Status, EventActivity, CaseEvent, Case


class CaseActionAdmin(admin.ModelAdmin):
    list_display=('id', 'description')
    list_filter = []
    


class CategoryAdmin(admin.ModelAdmin):
    list_display=('id','category','plural','default_status')
    list_filter = []
    


class PriorityAdmin(admin.ModelAdmin):
    list_display=('id', 'description','default')
    list_filter = []


    
class StatusAdmin(admin.ModelAdmin):
    list_display=('id', 'description', 'category')
    list_filter = ['category']
    radio_fields = {
        "category": admin.HORIZONTAL,
    }


    
class EventActivityAdmin(admin.ModelAdmin):
    list_display=('id', 'name','summary','category')
    list_filter = ['category']
    radio_fields = {
        "category": admin.HORIZONTAL,
    }


class CaseEventInline(admin.StackedInline):
    model = CaseEvent    

class CaseEventAdmin(admin.ModelAdmin):
    list_display=('id','notes','case','activity')
    list_filter = ['activity','case']



class CaseReversion(VersionAdmin):
    list_display=('title','orig_title','status','category', 'last_edit_by', 'last_edit_date','assigned_to')
    list_filter=['id','title','status','category','last_edit_by','assigned_to']
    
    fieldsets = (
                 ('Basic Information', { 'fields': ('title',
                                                    ('category','status','priority'),
                                                    'assigned_to',
                                                    'next_action',
                                                    'parent_case')
                                        }),
                 ('Activity Information', { 'fields': (('opened_by','opened_date'),
                                                       ('last_edit_by','last_edit_date'),
                                                       ('resolved_date','resolved_by'),
                                                       ('closed_date','closed_by'))
                                           })                 
                 )
    
    #radio_fields = {"priority": admin.VERTICAL,
    #                "category": admin.HORIZONTAL,
    #                "status": admin.VERTICAL,
    #                }
    #inlines = [ CaseEventInline, ]

admin.site.register(EventActivity, EventActivityAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(CaseAction, CaseActionAdmin)
admin.site.register(Priority, PriorityAdmin)
admin.site.register(Status, StatusAdmin)
admin.site.register(CaseEvent, CaseEventAdmin)
admin.site.register(Case, CaseReversion)
