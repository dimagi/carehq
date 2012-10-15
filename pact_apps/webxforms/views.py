# -*- coding: utf-8 -*-
from _collections import defaultdict
import re
from django.views.decorators.csrf import csrf_exempt
import os
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseBadRequest
import urllib2
import tempfile
import logging
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from casexml.apps.case.models import CommCareCase
from couchforms.util import post_xform_to_couch
from dimagi.utils.couch.safe_index import safe_index
from dimagi.utils.web import json_response
from pactcarehq.fixturegenerators import PACT_HP_GROUP_ID
from pactcarehq.models import PactUser
from pactpatient.models import PactPatient
from patient.models import Patient
from receiver.util import spoof_submission
from touchforms.formplayer.models import XForm
from touchforms.formplayer.views import enter_form
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
    #'http://dev.commcarehq.org/pact/progress_note': 'https://bitbucket.org/ctsims/commcare-pact/raw/tip/pact-app/pact_progress_note.xml',
    #'http://dev.commcarehq.org/pact/dots_form': 'https://bitbucket.org/ctsims/commcare-pact/raw/tip/pact-app/pact_dot_session.xml',
    #'http://dev.commcarehq.org/pact/bloodwork': 'https://bitbucket.org/ctsims/commcare-pact/raw/tip/pact-app/pact_bw_entry.xml',

    'http://dev.commcarehq.org/pact/progress_note': 'https://bitbucket.org/ctsims/commcare-pact/raw/tip/pact-app/twooh/pact_progress_note.xml',
    'http://dev.commcarehq.org/pact/dots_form': 'https://bitbucket.org/ctsims/commcare-pact/raw/tip/pact-app/twooh/pact_dot_session.xml',
    'http://dev.commcarehq.org/pact/bloodwork': 'https://bitbucket.org/ctsims/commcare-pact/raw/tip/pact-app/twooh/pact_bw_entry.xml',
    }

#from corehq.apps.app_manager.const import APP_V2, APP_V1
APP_V1 = '1'
APP_V2 = '2'
def _do_prep_form(request, case_id, xform_url, next_url, version=APP_V2, instance_data=None):
    if request.browser_info.get('ismobiledevice') == 'true':
        mode = 'touch'
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




    #cloudcare session_data
    if version == APP_V2:
        session_data = {'device_id': 'touchforms',
                        'app_version': '2.0',
                        'username': request.user.username,
                        'user_id': str(request.user.id),
                        'domain': 'pact',
        }
        if case_id:
            session_data["case_id"] = case_id
            session_data["pactid"] = pts[0].pact_id
    else:
        assert version == APP_V1
        # assume V1 / preloader structure
        session_data = {"meta": {"UserID":    str(request.user.id),
                                 "UserName":  request.user.username },
                        "property": {"deviceID": "touchforms"}}
        # check for a case id and update preloader appropriately
        if case_id:
            case = CommCareCase.get(case_id)
            session_data["case"] = case.get_preloader_dict()
            session_data["pactid"] = pts[0].pact_id

    #end cloudcare

    playsettings = defaultdict(lambda: "")

    playsettings["xform"] = get_remote_form(xform_url)
    playsettings["next"] = next_url
    #playsettings["data"] = json.dumps(preloaders)
    playsettings["input_mode"] = mode
    playsettings['instance'] = instance_data
    #new_form = fetch_xform_def(xform_url)
    formdef = fetch_xform_def(xform_url)
    #return enter_form(request, xform_id=new_form.id, onsubmit=touchform_callback, instance_xml=instance_data, input_mode=mode)

    #eturn play_remote(request, playsettings=playsettings)
    print "entering form"
    print session_data
    print instance_data
    return enter_form(request,
        xform_id=formdef.id,
        instance_xml=instance_data,
        input_mode=mode,
        onsubmit=touchform_callback_xml,
        session_data = session_data,
        )
#xform_id = kwargs.get('xform_id')
#xform = kwargs.get('xform')
#instance_xml = kwargs.get('instance_xml')
#session_data = coalesce(kwargs.get('session_data'), {})
#input_mode = coalesce(kwargs.get('input_mode'), 'touch')
#submit_callback = coalesce(kwargs.get('onsubmit'), default_submit)
#abort_callback = coalesce(kwargs.get('onabort'), default_abort)
#force_template = coalesce(kwargs.get('force_template'), None)




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
    try:
        case_id = orig_doc['form']['case']['@case_id']
    except KeyError:
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
        instance_data = XFormInstance.get_db().fetch_attachment(xform_id, "form.xml")
    except:
        raise Http404
        #return enter_form(request, xform_id=xform_def.id, onsubmit=callback, instance_xml=instance_data, input_mode=mode)
    return _do_prep_form(request, case_id, xform_url, reverse('touchform_callback', kwargs={'case_id': case_id}),
        instance_data=instance_data)
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
    reverse_back = reverse('view_pactpatient', kwargs={'patient_guid': patient_guid, 'view_mode': ''})
    return HttpResponseRedirect(reverse_back)



def touchform_callback_xml(xform, instance_xml):
    case_id_re = re.compile('<case_id>(?P<case_id>\w+)<\/case_id>')
    case_id_xml = case_id_re.search(instance_xml).group('case_id')
    #formsession = request.GET.get("session_id")
    print instance_xml
    #if formsession:
        #print "submit!"
    resp = spoof_submission(reverse("receiver_post"), instance_xml, hqsubmission=False)
    pts = PactPatient.view('pactpatient/by_case_id', key=case_id, include_docs=True).all()
    if len(pts) == 0:
        raise Http404
    patient_guid = pts[0]._id
    reverse_back = reverse('view_pactpatient', kwargs={'patient_guid': patient_guid, 'view_mode': ''})
    return HttpResponseRedirect(reverse_back)


def fetch_xform_def(xform_url):
    xform_str = get_remote_form(xform_url)
    try:
        form = XForm.from_raw(xform_str)
    except Exception, e:
        logging.error("Problem creating xform from %s: %s" % (file, e))
        raise e
    return form

#cloudcare stuffs
def get_owned_cases(django_user):
    """
    Get all cases in a domain owned by a particular user.
    """
    user = PactUser(str(django_user.id),
        django_user.username,
        django_user.password,
        django_user.date_joined,
        user_data = {'promoter_id': str(django_user.id), 'promoter_name': django_user.username, 'promoter_member_id': 'blah'},
        additional_owner_ids = [PACT_HP_GROUP_ID,]
    )
    try:
        owner_ids = user.get_owner_ids()
    except AttributeError:
        owner_ids = [user_id]
    keys = [[owner_id, False] for owner_id in owner_ids]
    cases = CommCareCase.view('case/by_owner_lite', keys=keys, include_docs=True, reduce=False)
    return [case.get_json() for case in cases]



@login_required
def get_cases(request):
    cases = get_owned_cases(request.user)
    if request.REQUEST:
        def _filter(case):
            for path, val in request.REQUEST.items():
                if safe_index(case, path.split("/")) != val:
                    return False
            return True
        print "filtering"
        cases = filter(_filter, cases)
    return json_response(cases)
