from django import template
from django.template.context import Context
from shinelabels.models import ZebraPrinter, ZebraStatus

register = template.Library()

bad_messages = [
    'head element out',
    'printer paused',
    'paper out',
    'ribbon out',
    'printhead over-temp',
    'printhead under-temp',
    'rewind full',
    'clean printhead',
    'replace head',
    'head open',
    'printer uptime heartbeat',
]

@register.simple_tag
def get_printer_status():
    ret = []
    for printer in ZebraPrinter.objects.all():
        status = ZebraStatus.objects.all().filter(printer=printer).exclude(status='pq job completed')
        is_active=False
        last_active = None
        last_inactive = None
        for stat in status:
            #this is pretty ghetto, but we kind of need to walk through it all due to the way in which the logs are recorded.
            if stat.status in bad_messages:
                is_active= stat.is_cleared
            if is_active:
                last_active=stat
            else:
                last_inactive = stat

        t = template.loader.get_template('shinelabels/printer_status.html')
        context_dict = dict()
        context_dict['status'] = is_active
        if is_active:
            context_dict['last'] = last_active
        else:
            context_dict['last'] = last_inactive
        context_dict['printer_name'] = "%s: %s" % (printer.location, printer.name)
        ret.append(t.render(Context(context_dict, autoescape=False)))
        return ''.join(ret)