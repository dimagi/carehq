from django import template
#from ashandapp.models import  CareTeam

register = template.Library()


#http://squeeville.com/2009/01/27/django-templatetag-requestcontext-and-inclusion_tag/

@register.inclusion_tag('ashandapp/site_navigation_menu.html', takes_context=True)
def navigation_menu(context):
    
    newcontext = {}
#    req = context['request']
#    if req.is_provider:
#        newcontext['patient_careteams'] = CareTeam.objects.filter(providers=req.provider)
#
#    newcontext['request'] = context['request']
    return newcontext
