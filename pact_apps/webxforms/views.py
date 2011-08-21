# -*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_exempt
import os
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
import urllib2
import tempfile
import logging
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from couchforms.util import post_xform_to_couch
from pactpatient.models import PactPatient
from patient.models.patientmodels import Patient
from touchforms.formplayer.models import XForm
from touchforms.formplayer.views import enter_form
from couchforms.models import XFormInstance
from webentry.util import get_remote_form

try:
    import simplejson as json
except:
    import json

def temp_landing(request):
    resp = HttpResponse()
    resp.write('<html><body><a href="/webxforms/progress_note/new/">New Progress Note</a></body></html>')
    return resp
    

def do_save_xform(xform):
    """
    Actually do a submission
    """
    pass

@login_required
@csrf_exempt
def edit_progress_note(request, doc_id):
    xform_url = 'http://build.dimagi.com/commcare/pact/pact_progress_note.xml'
    new_form = fetch_xform_def(xform_url)
    
    
    orig_doc = XFormInstance.get(doc_id)
    pact_id = orig_doc['form']['note']['pact_id']
    patient_doc_id = PactPatient.view('pactcarehq/patient_pact_ids', key=pact_id, include_docs=True).first()['_id']
    def callback(xform, doc):
        post_xform_to_couch(doc)
        reverse_back = reverse('view_pactpatient', kwargs={'patient_guid': patient_doc_id})
        return HttpResponseRedirect(reverse_back)

    try:
        instance_data = XFormInstance.get_db().fetch_attachment(doc_id,"form.xml")
    except:
        raise Http404
    return enter_form(request, xform_id=new_form.id, onsubmit=callback, instance_xml=instance_data, input_mode='type')

@login_required
@csrf_exempt
def edit_bloodwork(request, doc_id):
    xform_url = 'http://build.dimagi.com/commcare/pact/pact_bw_entry.xml'
    new_form = fetch_xform_def(xform_url)

    orig_doc = XFormInstance.get(doc_id)
    pact_id = orig_doc['form']['pact_id']
    patient_doc_id = PactPatient.view('pactcarehq/patient_pact_ids', key=pact_id, include_docs=True).first()['_id']
    def callback(xform, doc):
        post_xform_to_couch(doc)
        reverse_back = reverse('view_pactpatient', kwargs={'patient_guid': patient_doc_id})
        return HttpResponseRedirect(reverse_back)

    try:
        instance_data = XFormInstance.get_db().fetch_attachment(doc_id,"form.xml")
    except:
        raise Http404
    return enter_form(request, xform_id=new_form.id, onsubmit=callback, instance_xml=instance_data, input_mode='type')

def _new_form(request, patient_id, form):
    patient = Patient.objects.get(id=patient_id)
    pact_id = patient.couchdoc.pact_id
    case_id = patient.couchdoc.case_id
    preloader_data = {
        "case": {"case-id": case_id,
                 "pactid": pact_id,
                 },
        "property": { "DeviceID": "touchforms"},
        "meta": {
               "UserID": '%d' % (request.user.id),
               "UserName": request.user.username,
               }
    }
    
    def post_and_back_to_patient(xform, doc):
        post_xform_to_couch(doc)
        reverse_back = reverse('view_pactpatient', kwargs={'patient_guid': patient.doc_id})
        return HttpResponseRedirect(reverse_back)

    return enter_form(request, xform_id=form.id, onsubmit=post_and_back_to_patient, 
                      preloader_data=preloader_data, input_mode='type')
    
@login_required
@csrf_exempt
def new_progress_note(request, patient_id):
    """
    Fill out a NEW progress note
    """
    xform_url = 'http://build.dimagi.com/commcare/pact/pact_progress_note.xml'
    new_form = fetch_xform_def(xform_url)
    return _new_form(request, patient_id, new_form)
    
@login_required
@csrf_exempt
def new_bloodwork(request, patient_id): 
    """
    Fill out a NEW bloodwork
    """
    xform_url = 'http://build.dimagi.com/commcare/pact/pact_bw_entry.xml'
    new_form = fetch_xform_def(xform_url)
    return _new_form(request, patient_id, new_form)
    

def fetch_xform_def(xform_url):
    xform_str = get_remote_form(xform_url)
    try:
        tmp_file_handle, tmp_file_path = tempfile.mkstemp()
        tmp_file = os.fdopen(tmp_file_handle, 'w')
        tmp_file.write(xform_str.decode('utf-8').encode('utf-8'))
        tmp_file.close()
        new_form = XForm.from_file(tmp_file_path, str(file))
    except Exception, e:
        logging.error("Problem creating xform from %s: %s" % (file, e))
        raise e
    return new_form


