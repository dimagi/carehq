# -*- coding: utf-8 -*-
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
def edit_progress_note(request, doc_id):
    xform_url = 'http://build.dimagi.com/commcare/pact/pact_progress_note.xml'
    new_form = fetch_xform_def(xform_url)
    orig_doc = XFormInstance.get(doc_id)
    pact_id = orig_doc['form']['note']['pact_id']
    patient_id = PactPatient.view('pactcarehq/patient_pact_ids', key=pact_id, include_docs=True).first()['django_uuid']
    def callback(xform, doc):
        post_xform_to_couch(doc)
        reverse_back = reverse('view_patient', kwargs={'patient_id': patient_id})
        return HttpResponseRedirect(reverse_back)

    try:
        instance_data = XFormInstance.get_db().fetch_attachment(doc_id,"form.xml")
    except:
        raise Http404
    return enter_form(request, xform_id=new_form.id, onsubmit=callback, instance_xml=instance_data, input_mode='type')

@login_required
def edit_bloodwork(request, doc_id):
    xform_url = 'http://build.dimagi.com/commcare/pact/pact_bw_entry.xml'
    new_form = fetch_xform_def(xform_url)

    orig_doc = XFormInstance.get(doc_id)
    pact_id = orig_doc['form']['pact_id']
    patient_id = PactPatient.view('pactcarehq/patient_pact_ids', key=pact_id, include_docs=True).first()['django_uuid']
    def callback(xform, doc):
        post_xform_to_couch(doc)
        reverse_back = reverse('view_patient', kwargs={'patient_id': patient_id})
        return HttpResponseRedirect(reverse_back)

    try:
        instance_data = XFormInstance.get_db().fetch_attachment(doc_id,"form.xml")
    except:
        raise Http404
    return enter_form(request, xform_id=new_form.id, onsubmit=callback, instance_xml=instance_data, input_mode='type')

@login_required
def new_progress_note(request, patient_id): #patient_id
    """
    Fill out a NEW progress note
    """

    patient = Patient.objects.get(id=patient_id)
    pact_id = patient.couchdoc.pact_id
    case_id = patient.couchdoc.case_id

    def callback(xform, doc):
        post_xform_to_couch(doc)
        reverse_back = reverse('view_patient', kwargs={'patient_id': patient_id})
        return HttpResponseRedirect(reverse_back)


    xform_url = 'http://build.dimagi.com/commcare/pact/pact_progress_note.xml'
    new_form = fetch_xform_def(xform_url)

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

    return enter_form(request, xform_id=new_form.id, onsubmit=callback, preloader_data=preloader_data, input_mode='type')


def fetch_xform_def(xform_url):
    url_resp = urllib2.urlopen(xform_url)
    xform_str = url_resp.read()
    try:
        tmp_file_handle, tmp_file_path = tempfile.mkstemp()
        tmp_file = os.fdopen(tmp_file_handle, 'w')
        tmp_file.write(xform_str.decode('utf-8').encode('utf-8'))
        tmp_file.close()
        new_form = XForm.from_file(tmp_file_path, str(file))
        notice = "Created form: %s " % file
    except Exception, e:
        logging.error("Problem creating xform from %s: %s" % (file, e))
        success = False
        notice = "Problem creating xform from %s: %s" % (file, e)
        raise e
    return new_form


@login_required
def new_bloodwork(request, patient_id): #patient_id
    """
    Fill out a NEW bloodwork
    """

    patient = Patient.objects.get(id=patient_id)
    pact_id = patient.couchdoc.pact_id
    case_id = patient.couchdoc.case_id
    def callback(xform, doc):
        post_xform_to_couch(doc)
        reverse_back = reverse('view_patient', kwargs={'patient_id': patient_id})
        return HttpResponseRedirect(reverse_back)

    xform_url = 'http://build.dimagi.com/commcare/pact/pact_bw_entry.xml'
    new_form = fetch_xform_def(xform_url)

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
    return enter_form(request, xform_id=new_form.id, onsubmit=callback, preloader_data=preloader_data, input_mode='type')


