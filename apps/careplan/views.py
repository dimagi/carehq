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

from careplan.models import BasePlan, PlanCategory, PlanTag, BasePlanItem, PlanRule 
from careplan.models import CarePlanCaseLink, PlanItem, CarePlan



def all_template_items(request, template_name = "careplan/template_items.html"):
    context = {}    
    
    roots_only = False
    for item in request.GET.items():
        if item[0] == 'roots':
            roots_only=True
            
    if roots_only:            
        context['show_children'] = True
        context['plan_items'] = BasePlanItem.objects.all().filter(parent=None)
    else:
        context['show_children'] = False 
        context['plan_items'] = BasePlanItem.objects.all()
        
    return render_to_response(template_name, context,context_instance=RequestContext(request))

def view_template_item(request, template_id, template_name = "careplan/template_items.html"):
    context = {}    
    context['show_children'] = True
    context['plan_items'] = BasePlanItem.objects.filter(id=template_id)
    
    pi = BasePlanItem.objects.filter(id=template_id)[0]
    return render_to_response(template_name, context,context_instance=RequestContext(request))

