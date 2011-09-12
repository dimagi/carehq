from django.contrib.auth.decorators import login_required
from webentry.util import shared_preloaders, user_meta_preloaders, get_remote_form
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
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

def get_form(filename):
    path = os.path.join(os.path.dirname(__file__),"xforms", filename) 
    with open(path) as f:
        return f.read()

def random_barcode():
    # TODO: do this serially to ensure no conflicts?
    return datetime.now().strftime('%Y%m%d') + ''.join([random.choice(string.ascii_uppercase+string.digits) for i in range(8)])
    #return "%015d" % random.randint(0, 999999999999999)

def get_preloaders(request, patient_guid):
    preloaders = shared_preloaders()
    preloaders.update(user_meta_preloaders(request.user))
    preloaders["case"] = {"patient_guid": patient_guid}
    return preloaders

def get_playsettings(request, patient_guid, form_url, next=None, ua=None):
    """
    Get the player settings with some overrides
    """



@login_required
def clinical_information(request, patient_guid):
    """
    This is the initial bloodwork order request that goes out.  This scans the vial of blood barcode for record keeping as it is sent down to Lab1.
    """
    preloaders = get_preloaders(request, patient_guid)
    playsettings = defaultdict(lambda: "")
    playsettings["xform"] = get_remote_form("https://bitbucket.org/ctsims/commcare-sets/raw/tip/shine/blood_culture_questionnaire.xml")
    playsettings["next"] = reverse('new_bloodwork_order_cb', kwargs={'patient_guid': patient_guid})
    playsettings["data"] = json.dumps(preloaders)
    playsettings["input_mode"] = "type"
    return play_remote(request, playsettings=playsettings)



@login_required
def new_bloodwork_lab(request, case_id):
    pass


@login_required
def new_bloodwork_discharge(request, patient_guid):
    pass

@login_required
def discharge_cb(request, patient_guid):
    """
    A bloodwork entry is the fulfillment of a bloodwork order request.
    This is LAB1 filling out this stuff.
    """
    preloaders = shared_preloaders()
    preloaders.update(user_meta_preloaders(request.user))
    preloaders["case"] = {"case-id": case_id}
    playsettings = defaultdict(lambda: "")
    playsettings["xform"] = get_remote_form("https://bitbucket.org/ctsims/commcare-sets/raw/tip/shine/create_order.xml")
    playsettings["next"] = reverse('new_bloodwork_order_cb', kwargs={'case_id': case_id})
    playsettings["data"] = json.dumps(preloaders)
    playsettings["input_mode"] = "type"
    return play_remote(request, playsettings=playsettings)

    pass


@login_required
def new_bloodwork_entry(request, case_id):
    """
    A bloodwork entry is the fulfillment of a bloodwork order request.
    This is LAB1 filling out this stuff.
    """
    preloaders = shared_preloaders()
    preloaders.update(user_meta_preloaders(request.user))
    preloaders["case"] = {"case-id": case_id}
    playsettings = defaultdict(lambda: "")
    playsettings["xform"] = get_remote_form("https://bitbucket.org/ctsims/commcare-sets/raw/tip/shine/create_order.xml")
    playsettings["next"] = reverse('new_bloodwork_order_cb', kwargs={'case_id': case_id})
    playsettings["data"] = json.dumps(preloaders)
    playsettings["input_mode"] = "type"
    return play_remote(request, playsettings=playsettings)


@login_required
def new_bloodwork_order(request, case_id):
    """
    This is the initial bloodwork order request that goes out.  This scans the vial of blood barcode for record keeping as it is sent down to Lab1.
    """
    preloaders = shared_preloaders()
    preloaders.update(user_meta_preloaders(request.user))
    preloaders["case"] = {"case_id": case_id}
    playsettings = defaultdict(lambda: "")
    playsettings["xform"] = get_remote_form("https://bitbucket.org/ctsims/commcare-sets/raw/tip/shine/clinical_information.xml")
    playsettings["next"] = reverse('shine_form_cb', kwargs={'case_id': case_id})
    playsettings["data"] = json.dumps(preloaders)
    playsettings["input_mode"] = "type"
    return play_remote(request, playsettings=playsettings)


@login_required
def shine_form_cb(request, case_id):
    formsession = request.GET.get("session_id")
    if formsession:
        instance_xml = get_remote_instance(request, formsession).content
        resp = spoof_submission(reverse("receiver_post"), instance_xml, hqsubmission=False)

    casedoc = CommcareCase.get(case_id)

    reverse_back = reverse('shine_single_patient', kwargs={'patient_guid': casedoc.patient_guid })
    return HttpResponseRedirect(reverse_back)

@httpdigest
def ota_restore(request):
    user = ShineUser.from_django_user(request.user)
    restore_id = request.GET.get('since')
    response = generate_restore_payload(user, restore_id)
    return HttpResponse(response, mimetype="text/xml")
    