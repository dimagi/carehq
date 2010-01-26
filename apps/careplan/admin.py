from django.contrib import admin

from reversion.admin import VersionAdmin
from django.contrib.auth.models import User
from models import BasePlan, PlanCategory, PlanTag, BasePlanItem, PlanRule
from models import PlanItem, CarePlan
#from casetracker.admin import CaseInline

class PlanCategoryAdmin(admin.ModelAdmin):
    list_display = ('name','description')
admin.site.register(PlanCategory, PlanCategoryAdmin)

class PlanTagAdmin(admin.ModelAdmin):
    list_display = ('id','tag',)
admin.site.register(PlanTag, PlanTagAdmin)

class PlanRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description','module','method')
    list_filter = ['module',]
admin.site.register(PlanRule, PlanRuleAdmin)

#class PlanItemInline(admin.StackedInline):
#    model = PlanItem

class PlanItemAdmin(admin.ModelAdmin):
    list_display = ('name','description','parent', 'from_template')
    list_filter = ['from_template','parent']
    #inlines = [CaseInline,]
admin.site.register(PlanItem, PlanItemAdmin)



class CarePlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'patient','version','from_template', 'created_by', 'created_date', 'modified_by', 'modified_date')
    list_filter = ['created_by', 'modified_by', 'from_template', 'patient']    
    #inlines = [ PlanItemInline, ]
admin.site.register(CarePlan, CarePlanAdmin)

#class BasePlanItemInline(admin.StackedInline):
#    model = BasePlanItem

class BasePlanItemAdmin(admin.ModelAdmin):
    list_display = ('indent_name', 'name', 'description','parent')
    list_filter = ['parent']    
admin.site.register(BasePlanItem, BasePlanItemAdmin)


class BasePlanAdmin(admin.ModelAdmin):
    list_display=('title', 'version', 'created_by', 'created_date', 'modified_by', 'modified_date')
    list_filter = ['created_by', 'modified_by']    
    #inlines = [ BasePlanItemInline, ]
admin.site.register(BasePlan, BasePlanAdmin)
