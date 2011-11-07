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
from receiver.util import spoof_submission
from touchforms.formplayer.models import XForm
from touchforms.formplayer.views import enter_form, play_remote, get_remote_instance
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

def _do_prep_form(request, case_id, xform_url, next_url, instance_data=None):
    if request.browser_info.get('ismobiledevice') == 'true':
        mode='touch'
    else:
        #do one more check
        ua_string = request.META['HTTP_USER_AGENT']
        if ua_string.count('Android') > 0:
            mode = 'touch'
        else:
            mode = 'type'

    if request.GET.get('override', None) is not None:
        mode = request.GET['override']

    pts = PactPatient.view('pactpatient/by_case_id', key=case_id, include_docs=True).all()
    if len(pts) == 0:
        raise Http404

    preloaders = shared_preloaders()
    preloaders.update(user_meta_preloaders(request.user))
    preloaders['case'] = {
        'case-id': case_id,
        "pactid": pts[0].pact_id,
        }
    playsettings = defaultdict(lambda:"")

    playsettings["xform"] = get_remote_form(xform_url)
    playsettings["next"] = next_url
    playsettings["data"] = json.dumps(preloaders)
    playsettings["input_mode"] = mode
    playsettings['instance'] = instance_data
    #new_form = fetch_xform_def(xform_url)
    #return enter_form(request, xform_id=new_form.id, onsubmit=touchform_callback, instance_xml=instance_data, input_mode=mode)

    return play_remote(request, playsettings=playsettings)


@login_required
@csrf_exempt
def new_xform_interaction(request, case_id, interaction):
    """
    This is the initial bloodwork order request that goes out.  This scans the vial of blood barcode for record keeping as it is sent down to Lab1.
    """
    xform_url = interaction_url_map.get(interaction, None)

    #basic sanity check for our data existing
    if not xform_url:
        raise Http404

    return _do_prep_form(request, case_id, xform_url, reverse('touchform_callback', kwargs={'case_id': case_id}))


@login_required
@csrf_exempt
def edit_xform_interaction(request, xform_id):
    orig_doc = XFormInstance.get(xform_id)
    xform_url = xmlns_url_map.get(orig_doc.xmlns, None)
    case_id = orig_doc['form']['case']['case_id']
    pts = PactPatient.view('pactpatient/by_case_id', key=case_id, include_docs=True).all()

    if xform_url is None:
        raise Http404
    if len(pts) == 0:
        raise Http404

    xform_def = fetch_xform_def(xform_url) # get existing data
    pt = pts[0]
    patient_doc_id = pt._id
#    def callback(xform, doc):
#        post_xform_to_couch(doc)
#        reverse_back = reverse('view_pactpatient', kwargs={'patient_guid': patient_doc_id})
#        return HttpResponseRedirect(reverse_back)

    try:
        instance_data = XFormInstance.get_db().fetch_attachment(xform_id,"form.xml")
    except:
        raise Http404
    #return enter_form(request, xform_id=xform_def.id, onsubmit=callback, instance_xml=instance_data, input_mode=mode)
    return _do_prep_form(request, case_id, xform_url, reverse('touchform_callback', kwargs={'case_id': case_id}), instance_data=instance_data)
    #return enter_form(request, xform_id=form.id, onsubmit=post_and_back_to_patient,  preloader_data=preloader_data, input_mode='type')


@login_required
@csrf_exempt
def touchform_callback(request, case_id):
    formsession = request.GET.get("session_id")
    if formsession:
        instance_xml = get_remote_instance(request, formsession).content
        resp = spoof_submission(reverse("receiver_post"), instance_xml, hqsubmission=False)
    pts = PactPatient.view('pactpatient/by_case_id', key=case_id, include_docs=True).all()
    if len(pts) == 0:
        raise Http404
    patient_guid = pts[0]._id
    reverse_back = reverse('view_pactpatient', kwargs={'patient_guid': patient_guid})
    return HttpResponseRedirect(reverse_back)

def fetch_xform_def(xform_url):
    xform_str = get_remote_form(xform_url)
    try:
        tmp_file_handle, tmp_file_path = tempfile.mkstemp()
        tmp_file = os.fdopen(tmp_file_handle, 'w')
        #tmp_file.write(xform_str.decode('utf-8').encode('utf-8'))
        tmp_file.write(xform_str)#.decode('utf-8').encode('utf-8'))
        tmp_file.close()
        new_form = XForm.from_file(tmp_file_path, str(file))
    except Exception, e:
        logging.error("Problem creating xform from %s: %s" % (file, e))
        raise e
    return new_form

