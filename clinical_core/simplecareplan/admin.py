from django.contrib import admin
from models import *

class CarePlanAdmin(admin.ModelAdmin):
    list_display=('patient',)
    list_filter = ['patient',]
admin.site.register(CarePlan, CarePlanAdmin)


class CarePlanElementAdmin(admin.ModelAdmin):
    list_display=('name',)
    list_filter = ['name',]
admin.site.register(CarePlanElement, CarePlanElementAdmin)

