from django import template
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.template import Context, Template

from datetime import datetime
register = template.Library() 
 
@register.simple_tag 
def time_interval(date):
    if date > datetime.utcnow():
        timedelta_string = "timeuntil"
        time_suffix = "from now"
    else:
        timedelta_string = "timesince"
        time_suffix = "ago"
        
    t = Template("{{ dateval|%s:utcnow }}" % (timedelta_string))
    c = Context({"dateval": date, "utcnow":datetime.utcnow() })
    
    datestring = t.render(c).split(',')[0] + " " + time_suffix
    return datestring