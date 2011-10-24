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
        states = ZebraStatus.objects.all().filter(printer=printer).filter(status='printer uptime heartbeat').order_by('-event_date')

        if states[0].is_cleared:
            is_active=True
        else:
            is_active=False

        last_active = None
        last_inactive = None
        for stat in states[1:]:
            if is_active:
                if not stat.is_cleared:
                    last_inactive = stat
                    break
            else:
                if stat.is_cleared:
                    last_active = stat
                    break
        print last_active
        print last_inactive
        print is_active
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