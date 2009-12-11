import logging
import hashlib
import settings
import traceback
import sys
import os
import uuid
import string
from datetime import timedelta

from django.http import HttpResponse
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.exceptions import *
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_http_methods
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

# myapp/views.py
from datagrids import UserDataGrid
 
def datagrids(request, template_name='ashandapp/datagrids.html'):
    return UserDataGrid(request).render_to_response(template_name)

def styleguide(request, template_name="ashandapp/styleguide.html"):
    context = {}
    return render_to_response(template_name, context)