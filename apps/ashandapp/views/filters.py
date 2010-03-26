from datetime import datetime
import logging

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponse
from casetracker.models import Filter, Case, CaseEvent

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from provider.models import Provider


from ashandapp.models import CareTeam, ProviderRole, ProviderLink, CaregiverLink, CareRelationship, FilterProfile

from ashandapp.forms.question import NewQuestionForm
from ashandapp.forms.issue import NewIssueForm
from ashandapp.templatetags.filter_tags import case_column_plain
from ashandapp.views.cases import queries

def process_filter_change(request):
    """
    From the main toolbar, case filters will be changed/chosen from the pulldown.
    The POST will put put the filter/query ID into the request, and put a POST in here.
    then, the viewprofile object will update with the case filter for them to see when they click back on the "case list"  
    """
    pass