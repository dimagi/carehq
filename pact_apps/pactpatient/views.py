# Create your views here.
import pdb
import simplejson
import uuid
from django.contrib.auth.decorators import  login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, HttpResponse, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.core.cache import cache
from django_digest.decorators import httpdigest
from carehq_core import carehq_constants, carehq_api
from casexml.apps.case.models import CommCareCase
from pactpatient.forms import PactPatientForm
from pactpatient.models.pactmodels import PactPatient
from patient.models import Patient
import urllib
from patient.models import CPhone
from datetime import datetime, datetime
import logging
from django.contrib import messages
from permissions.models import PrincipalRoleRelation, Actor, Role


def get_chw_pt_permissions(from_cache=True):
    """
    Hackish cache for chw/patient permissions for primary permissions.
    """
    if from_cache:
        pt_chw_map = simplejson.loads(cache.get("pactpatient_primary_hps",'{}'))
        if pt_chw_map is not '':
            return pt_chw_map
    return set_chw_pt_permissions()

def set_chw_pt_permissions():
    """
    Forcibly set the cache of the primary_hp property for the patient documents.
    """
    raw_map_list = PactPatient.view('pactcarehq/chw_assigned_patients').all()
    pt_chw_map = {}
    for x in raw_map_list:
        subarr = pt_chw_map.get(x['id'], [])
        subarr.append(x['key'])
        pt_chw_map[x['id']] = subarr
    cache.set("pactpatient_primary_hps", simplejson.dumps(pt_chw_map))
    return pt_chw_map


def recompute_chw_actor_permissions(patient_doc, old_map_full=None):
    """
    Once the primary hp is reset, need to recompute all the actor permissions for the patients and the CHWs.
    """
    #invalidate the schedule cache
    patient_doc.get_ghetto_schedule_xml(invalidate=True)
    if old_map_full is None:
        old_map = get_chw_pt_permissions().get(patient_doc._id, [])
    else:
        old_map=old_map_full.get(patient_doc._id, [])
    new_map = get_chw_pt_permissions(from_cache=False).get(patient_doc._id, [])
    removed = set(old_map).difference(set(new_map))
    added = set(new_map).difference(set(old_map))

    all_prrs = PrincipalRoleRelation.objects.filter(content_type=ContentType.objects.get_for_model(Patient), content_id=patient_doc.django_uuid)

    for prr in all_prrs.filter(actor__user__username__in=removed):
        carehq_api.remove_from_careteam(patient_doc, prr.actor.actordoc, prr.role)

    for username in added:
        #find the Actor that has the appropriate Global CHW role
        #ugh, interesting, so this is a permissions issue on whether or not they're a chw
        django_actor_qset = Actor.objects.filter(principal_roles__role__name=carehq_constants.role_chw, user__username=username)
        if django_actor_qset.count() > 0:
            if django_actor_qset.count() != 1:
                logging.error("Error, a principal role relation cannot be in duplicate for a given (actor, role, content) triplet (%s, %s, %s" % (username, carehq_constants.role_chw, patient_doc))
            django_actor=django_actor_qset[0]
            carehq_api.add_to_careteam(patient_doc, django_actor.actordoc, Role.objects.get(name=carehq_constants.role_primary_chw))
    set_chw_pt_permissions()



@login_required
def new_patient(request, template_name="pactpatient/new_pactpatient.html"):
    context = RequestContext(request)
    if request.method == 'POST':
        form = PactPatientForm("new", data=request.POST)
        #make patient
        if form.is_valid():
            old_map_full = get_chw_pt_permissions(from_cache=False)
            newptdoc = form.save(commit=False)
            newptdoc.case_id = uuid.uuid4().hex
            newptdoc.save()
            #now create a case for this
            case = CommCareCase()
            case._id = newptdoc.case_id
            case.start_date = datetime.utcnow().date()
            case.external_id = newptdoc.pact_id
            case.save()
            messages.add_message(request, messages.SUCCESS, "Added patient " + form.cleaned_data['first_name'] + " " + form.cleaned_data['last_name'])
            recompute_chw_actor_permissions(newptdoc, old_map_full=old_map_full)
            return HttpResponseRedirect(reverse('view_pactpatient', kwargs={'patient_guid':newptdoc._id}))
        else:
            messages.add_message(request, messages.ERROR, "Failed to add patient!")
            context['patient_form'] = form
    else:
        #if it's a regular get, let's cache the results of the PactPatient view
        #set_chw_pt_permissions()
        context['patient_form'] = PactPatientForm("new")

    return render_to_response(template_name, context_instance=context)
