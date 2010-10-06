# Create your views here.
from django.contrib.auth.decorators import permission_required
import json
from django.http import HttpResponseRedirect
from patient.models.couchmodels import CPhone, CAddress
import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response


