# -*- coding: utf-8 -*-
from _collections import defaultdict
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
from touchforms.formplayer.views import enter_form, play_remote
from couchforms.models import XFormInstance
from webentry.util import get_remote_form, shared_preloaders, user_meta_preloaders

try:
    import simplejson as json
except:
    import json

interaction_url_map = {
    'progress_note': 'https://bitbucket.org/ctsims/commcare-pact/raw/tip/pact-app/pact_progress_note.xml',
    'dot': 'https://bitbucket.org/ctsims/commcare-pact/raw/tip/pact-app/pact_dot_session.xml',
    'bloodwork': 'https://bitbucket.org/ctsims/commcare-pact/raw/tip/pact-app/pact_bw_entry.xml',
    }

xmlns_url_map = {
    'http://dev.commcarehq.org/pact/progress_note': 'https://bitbucket.org/ctsims/commcare-pact/raw/tip/pact-app/pact_progress_note.xml',
    'http://dev.commcarehq.org/pact/dots_form': 'https://bitbucket.org/ctsims/commcare-pact/raw/tip/pact-app/pact_dot_session.xml',
    'http://dev.commcarehq.org/pact/bw': 'https://bitbucket.org/ctsims/commcare-pact/raw/tip/pact-app/pact_bw_entry.xml',
    }
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



@login_required
@csrf_exempt
def new_dots(request, patient_id):
    """
    Fill out a NEW DOTS
    """
    xform_url = 'http://build.dimagi.com/commcare/pact/pact_dot_session.xml'
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


###########################33
#Newer shine code



form_url_map = {
    'Clinical Info': 'https://bitbucket.org/ctsims/commcare-sets/raw/tip/shine/clinical_information.xml',
#    'Follow Up': 'https://bitbucket.org/ctsims/commcare-sets/raw/tip/shine/clinical_information.xml',
    'Lab Data': 'https://bitbucket.org/ctsims/commcare-sets/raw/tip/shine/survey_lab_data.xml',
    'Emergency Lab': 'https://bitbucket.org/ctsims/commcare-sets/raw/tip/shine/lab_one.xml',
    'Biochemical Lab': 'https://bitbucket.org/ctsims/commcare-sets/raw/tip/shine/lab_two.xml',
    'Speciation': 'https://bitbucket.org/ctsims/commcare-sets/raw/tip/shine/lab_three.xml',
    'Sensitivity': 'https://bitbucket.org/ctsims/commcare-sets/raw/tip/shine/lab_four.xml',
    'Outcome': 'https://bitbucket.org/ctsims/commcare-sets/raw/tip/shine/clinical_outcome.xml',
}

@login_required
@csrf_exempt
def edit_interaction(request, patient_doc, xform_id):
    xform_url = xform_url_map() #get the xform location
    new_form = fetch_xform_def(xform_url) # get existing data
    orig_doc = XFormInstance.get(doc_id)
    patient_doc_id = patient_doc._id
    def callback(xform, doc):
        post_xform_to_couch(doc)
        reverse_back = reverse('view_pactpatient', kwargs={'patient_guid': patient_doc_id})
        return HttpResponseRedirect(reverse_back)

    try:
        instance_data = XFormInstance.get_db().fetch_attachment(doc_id,"form.xml")
    except:
        raise Http404
    return enter_form(request, xform_id=new_form.id, onsubmit=callback, instance_xml=instance_data, input_mode='type')



def _get_preloaders(request, patient_guid):
    preloaders = shared_preloaders()
    preloaders.update(user_meta_preloaders(request.user))
    preloaders["case"] = {"patient_guid": patient_guid}
    return preloaders


def _prep_form(request, case_id, xform_url, next_url, mode):

    if request.browser_info.get('ismobiledevice') == 'true':
        mode='touch'
    else:
        #do one more check
        ua_string = request.META['HTTP_USER_AGENT']
        if ua_string.count('Android') > 0:
            mode = 'touch'
        else:
            mode = 'type'
    preloaders = shared_preloaders()
    preloaders.update(user_meta_preloaders(request.user))
    preloaders['case'] = {'case-id': case_id}
    playsettings = defaultdict(lambda:"")

    playsettings["xform"] = get_remote_form(xform_url)
    playsettings["next"] = next_url
    playsettings["data"] = json.dumps(preloaders)
    playsettings["input_mode"] = mode
    return play_remote(request, playsettings=playsettings)


@login_required
def new_xform_interaction(request, case_id, interaction):
    """
    This is the initial bloodwork order request that goes out.  This scans the vial of blood barcode for record keeping as it is sent down to Lab1.
    """
    pts = ShinePatient.view('shinepatient/patient_cases_all', key=case_id, include_docs=True).all()
    if len(pts) == 0:
        raise Http404
    patient_guid = pts[0]._id


    xform_url = form_url_map.get(interaction, None)
    if xform_url is None:
        raise Http404
    return _prep_form(request, case_id,
                     xform_url,
                     reverse('shine_form_cb', kwargs={'case_id': case_id}), 'type')


@login_required
def shine_form_cb(request, case_id):
    formsession = request.GET.get("session_id")
    if formsession:
        instance_xml = get_remote_instance(request, formsession).content
        resp = spoof_submission(reverse("receiver_post"), instance_xml, hqsubmission=False)
    pts = ShinePatient.view('shinepatient/patient_cases_all', key=case_id, include_docs=True).all()
    if len(pts) == 0:
        raise Http404
    patient_guid = pts[0]._id

    reverse_back = reverse('shine_single_patient', kwargs={'patient_guid': patient_guid})
    return HttpResponseRedirect(reverse_back)

