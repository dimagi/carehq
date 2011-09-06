from django.contrib import admin
from shinelabels.models import ZebraPrinter, ZebraStatus, LabelQueue

class ZPrinterAdmin(admin.ModelAdmin):
    list_display = ('name','ip_address', 'port', 'location','serial_number')
    list_filter = []
admin.site.register(ZebraPrinter, ZPrinterAdmin)


class LabelQueueAdmin(admin.ModelAdmin):
    list_display=('created_date', 'destination', 'fulfilled_date')
    list_filter=['destination']
admin.site.register(LabelQueue, LabelQueueAdmin)


class ZebraStatusAdmin(admin.ModelAdmin):
    list_display=('event_date','printer', 'status','is_triggered')
    list_filter = ['printer','status']
admin.site.register(ZebraStatus, ZebraStatusAdmin)

