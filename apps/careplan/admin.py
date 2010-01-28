from django.contrib import admin

from reversion.admin import VersionAdmin
from django.contrib.auth.models import User
from models import TemplateCarePlan, PlanCategory, PlanTag, TemplateCarePlanItem, PlanRule, TemplateCarePlanItemLink
from models import CarePlanItem, CarePlan, CarePlanCaseLink, CarePlanItemLink
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

class CarePlanCaseInline(admin.ModelAdmin):
    list_display=('case','careplan_item')
    list_filter = ['careplan_item']
admin.site.register(CarePlanCaseLink, CarePlanCaseInline)

class CarePlanItemInline(admin.StackedInline):
    model = CarePlanItemLink

class CarePlanItemAdmin(admin.ModelAdmin):
    list_display = ('name','description','parent', 'from_template')
    list_filter = ['from_template','parent']    
admin.site.register(CarePlanItem, CarePlanItemAdmin)

class CarePlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'patient','version','from_template', 'created_by', 'created_date', 'modified_by', 'modified_date')
    list_filter = ['created_by', 'modified_by', 'from_template', 'patient']    
    inlines = [CarePlanItemInline,]
admin.site.register(CarePlan, CarePlanAdmin)

###########################################################
#Region for Template Care plans and their related models

class TemplateCarePlanItemAdmin(admin.ModelAdmin):
    list_display = ('indent_name', 'name', 'description','parent')
    list_filter = ['parent']    
admin.site.register(TemplateCarePlanItem, TemplateCarePlanItemAdmin)

class TemplateCarePlanItemInline(admin.StackedInline):
    model = TemplateCarePlanItemLink

class TemplateCarePlanAdmin(admin.ModelAdmin):
    list_display=('title', 'version', 'created_by', 'created_date', 'modified_by', 'modified_date')
    list_filter = ['created_by', 'modified_by']    
    inlines = [ TemplateCarePlanItemInline, ]
admin.site.register(TemplateCarePlan, TemplateCarePlanAdmin)

############################################################