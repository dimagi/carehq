from django import template
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.template import Context, Template

from casetracker.models import Case
from casetracker.models import ActivityClass, CaseEvent, Status, CaseAction, Category
from ashandapp.models import CareTeamCaseLink, CareTeam
from datetime import datetime
register = template.Library()


#http://squeeville.com/2009/01/27/django-templatetag-requestcontext-and-inclusion_tag/

@register.inclusion_tag('ashandapp/site_navigation_menu.html', takes_context=True)
def navigation_menu(context):
    
    newcontext = {}
    req = context['request']
    if req.is_provider:
        newcontext['patient_careteams'] = CareTeam.objects.filter(providers=req.provider)
    
    newcontext['request'] = context['request']
    return newcontext
