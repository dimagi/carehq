from django import template
from dimagi.utils.make_time import make_time

register = template.Library()
from datetime import datetime,date

#http://squeeville.com/2009/01/27/django-templatetag-requestcontext-and-inclusion_tag/
@register.inclusion_tag('carehqapp/site_navigation_menu.html', takes_context=True)
def navigation_menu(context):
    newcontext = {}
    return context


@register.simple_tag
def get_timeago(data):
    if isinstance(data, datetime):
        return '<abbr class="timeago" title="%s"></abbr>' % data.strftime("%Y-%m-%dT%H:%M:%SZ")
    elif isinstance(data, date):
        return '<abbr class="timeago" title="%s"></abbr>' % data.strftime("%Y-%m-%dT%00:00:00Z")
    else:
        return '<abbr class="timeago" title="%s"></abbr>' % make_time().strftime("%Y-%m-%dT%00:00:00Z")

