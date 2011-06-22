from webentry.util import shared_preloaders, user_meta_preloaders
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

def get_form(filename):
    path = os.path.join(os.path.dirname(__file__),"xforms", filename) 
    with open(path) as f:
        return f.read()

def random_barcode():
    # TODO: do this serially to ensure no conflicts?
    return "%015d" % random.randint(0, 999999999999999)

def touchforms_callback(request, patient_id):
    formsession = request.GET.get("session_id")
    if formsession:
        instance_xml = get_remote_instance(request, formsession).content
        resp = spoof_submission(reverse("receiver_post"), instance_xml, hqsubmission=False)
        # TODO: communicate anything here?
           
    reverse_back = reverse('shine_single_patient', kwargs={'patient_id': patient_id})
    return HttpResponseRedirect(reverse_back)
        

def new_item_registration(request, patient_id):
    
    preloaders = shared_preloaders()
    preloaders.update(user_meta_preloaders(request.user))
    preloaders["case"] = {"patient_id": patient_id}
    preloaders["shine"] = {"barcode": random_barcode()}
    playsettings = defaultdict(lambda: "")
    playsettings["xform"] = get_form("item_register.xml")
    playsettings["next"] = reverse('shineforms_callback', kwargs={'patient_id': patient_id})
    playsettings["data"] = json.dumps(preloaders)
    playsettings["input_mode"] = "type"
    return play_remote(request, playsettings=playsettings)
    
@httpdigest
def ota_restore(request):
    user = ShineUser.from_django_user(request.user)
    restore_id = request.GET.get('since')
    response = generate_restore_payload(user, restore_id)
    return HttpResponse(response, mimetype="text/xml")
    