from django.contrib.auth.decorators import login_required
from shinepatient.models import ShinePatient
from webentry.util import shared_preloaders, user_meta_preloaders, get_remote_form
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from touchforms.formplayer.views import play_remote, get_remote_instance
from collections import defaultdict
import os
import json
from receiver.util import spoof_submission
from django_digest.decorators import *
import random
from casexml.apps.phone.models import User
from shineforms.models import ShineUser
from casexml.apps.phone.restore import generate_restore_payload
import string
from datetime import datetime


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

def get_form(filename):
    path = os.path.join(os.path.dirname(__file__), "xforms", filename)
    with open(path) as f:
        return f.read()


def random_barcode():
    # TODO: do this serially to ensure no conflicts?
    return datetime.now().strftime('%Y%m%d') + ''.join(
        [random.choice(string.ascii_uppercase + string.digits) for i in range(8)])
    #return "%015d" % random.randint(0, 999999999999999)


def _get_preloaders(request, patient_guid):
    preloaders = shared_preloaders()
    preloaders.update(user_meta_preloaders(request.user))
    preloaders["case"] = {"patient_guid": patient_guid}
    return preloaders


def _prep_form(request, case_id, xform_url, next_url, mode, instance_data=None):

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

    preloaders = shared_preloaders()
    preloaders.update(user_meta_preloaders(request.user))
    preloaders['case'] = {'case-id': case_id}
    playsettings = defaultdict(lambda:"")

    playsettings["xform"] = get_remote_form(xform_url)
    playsettings["next"] = next_url
    playsettings["data"] = json.dumps(preloaders)
    playsettings["input_mode"] = mode
    playsettings['instance'] = instance_data
    return play_remote(request, playsettings=playsettings)


@login_required
def new_mepi_interaction(request, case_id, interaction):
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

    reverse_back = reverse('shine_single_patient', kwargs={'patient_guid': patient_guid, 'view_mode': ''})
    return HttpResponseRedirect(reverse_back)

@httpdigest
def ota_restore(request):
    user = ShineUser.from_django_user(request.user)

    restore_id = request.GET.get('since')
    response = generate_restore_payload(user, restore_id)
    return HttpResponse(response, mimetype="text/xml")
