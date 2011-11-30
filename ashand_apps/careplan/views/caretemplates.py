import logging
import settings
import traceback
import sys
import os
import uuid
import string
from datetime import datetime, timedelta

from django.http import HttpResponse,Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.models import User 

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page

from careplan.models import TemplateCarePlan, PlanCategory, PlanTag, TemplateCarePlanItem, PlanRule 
#from careplan.models import CarePlanCaseLink, CarePlanItem, CarePlan



#see all care plans or template care plans
def all_careplans(request, template_name = "careplan/all_careplans.html"):
    context = {}    
    context['show_children'] = True
    context['careplans'] = TemplateCarePlan.objects.all()    
    return render_to_response(template_name, context,context_instance=RequestContext(request))


#see individual care plan or template careplan
def single_careplan(request, plan_id, template_name="careplan/view_careplan.html"):
    context = {}
    context['show_children'] = True    
    context['careplan'] = TemplateCarePlan.objects.get(id=plan_id)
    context['plan_items'] = context['careplan'].templatecareplanitemlink_set.all()    
    return render_to_response(template_name, context,context_instance=RequestContext(request))


def all_careplan_items(request, template_name = "careplan/careplan_items.html"):
    context = {}    
    roots_only = False
    for item in request.GET.items():
        if item[0] == 'roots':
            roots_only=True
            
    if roots_only:            
        context['show_children'] = True
        context['plan_items'] = TemplateCarePlanItem.objects.all().filter(parent=None)
    else:
        context['show_children'] = False 
        context['plan_items'] = TemplateCarePlanItem.objects.all()
        
    return render_to_response(template_name, context,context_instance=RequestContext(request))

# see individual careplan_item or template careplan_item
def single_careplan_item(request, item_id, template_name = "careplan/careplan_items.html"):
    context = {}    
    context['show_children'] = True
    context['plan_items'] = TemplateCarePlanItem.objects.filter(id=item_id)    
    return render_to_response(template_name, context,context_instance=RequestContext(request))






