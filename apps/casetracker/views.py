import logging
import hashlib
import settings
import traceback
import sys
import os
import uuid
import string
from datetime import timedelta

from django.http import HttpResponse,Http404
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.db import transaction
from django.db.models.query_utils import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.models import User 
from django.contrib.contenttypes.models import ContentType

from django.shortcuts import render_to_response

from models import Case, CaseEvent, Filter, GridPreference

from datagrids import CaseDataGrid, CaseEventDataGrid


def all_cases(request, template_name="casetracker/case_datagrid.html"):
    context = {}
    return CaseDataGrid(request).render_to_response(template_name)    

def view_case(request, case_id, template_name='casetracker/view_case.html'):
    context = {}
    return render_to_response(context, template_name)
    


def all_case_events(request, template_name='casetracker/case_event_datagrid.html'):
    return CaseEventDataGrid(request).render_to_response(template_name)
 
def view_case_events(request, case_id, template_name='casetracker/view_case_event.html'):
    context = {}
    return render_to_response(context, template_name)
    

def all_filters(request, template_name='casetracker/all_filters.html'):
    context = {}
    return render_to_response(context, template_name)
    

def view_filter(request, filter_id):
    context = {}
    showfilter = False
    for item in request.GET.items():
        if item[0] == 'filterinfo':
            showfilter = True
    
    if showfilter:
        template_name = "casetracker/show_filter.html"
        return render_to_response(context, template_name)
    else:
        #get the filter from the db
        filter = Filter.objects.get(id=filter_id)
        gridpref = GridPreference.objects.get(filter=filter)
        template_name='casetracker/case_datagrid.html'        
        return CaseDataGrid(request, gridpref=gridpref).render_to_response(template_name)
    

