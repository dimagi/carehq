# To manage patient views for create/view/update you need to implement them directly in your patient app
from _collections import defaultdict
from datetime import datetime
import logging
import re
import urllib
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from sorl.thumbnail.shortcuts import get_thumbnail
from clinical_core.webentry.util import get_remote_form, user_meta_preloaders, shared_preloaders
from couchforms.models import XFormInstance
from couchforms.util import post_xform_to_couch
from patient.models import Patient
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from patient.models import BasePatient
from patient.forms import BasicPatientForm
from django.contrib import messages
from receiver.util import spoof_submission
from shineforms.views import random_barcode
from shinepatient.models import ShinePatient
from casexml.apps.case.models import CommCareCase
import json
from couchdbkit.resource import ResourceNotFound
from patient.views import PatientListView
from slidesview.models import ImageAttachment
from touchforms.formplayer.views import play_remote, get_remote_instance


@login_required
def new_patient_touch(request):
    preloaders = shared_preloaders()
    preloaders.update(user_meta_preloaders(request.user))
    playsettings = defaultdict(lambda: "")
    playsettings["xform"] = get_remote_form("https://bitbucket.org/ctsims/commcare-sets/raw/752395978bb2/shine/patient_registration.xml")
    playsettings["next"] = reverse('newshinepatient_callback')
    playsettings["data"] = json.dumps(preloaders)
    playsettings["input_mode"] = "type"
    return play_remote(request, playsettings=playsettings)


@login_required
def newpatient_callback(request):
    formsession = request.GET.get("session_id")
    patient_id=None
    if formsession:
        instance_xml = get_remote_instance(request, formsession).content
        uid_re = re.compile('<uid>(?P<doc_id>\w+)<\/uid>')
        doc_id = uid_re.search(instance_xml).group('doc_id')
        resp = spoof_submission(reverse("receiver_post"), instance_xml, hqsubmission=False)
        #post_xform_to_couch(instance_xml)
        xform_doc = XFormInstance.get(doc_id)
        case_id = xform_doc['form']['case']['case_id']
        case_doc = CommCareCase.get(case_id)
        patient_guid = case_doc['patient_guid']

    if doc_id != None:
        reverse_back = reverse('shine_single_patient', kwargs={'patient_guid': patient_guid})
    else:
        raise Exception()
    return HttpResponseRedirect(reverse_back)
#
#@login_required
#def new_patient_django(request):
#    context = RequestContext(request)
#    if request.method == 'POST':
#        form = BasicPatientForm(data=request.POST)
#        # make patient
#        if form.is_valid():
#            newptdoc = ShinePatient()
#            newptdoc.patient_id = form.cleaned_data['patient_id']
#            newptdoc.gender = form.cleaned_data['gender']
#            newptdoc.birthdate = form.cleaned_data['birthdate']
#            newptdoc.first_name = form.cleaned_data['first_name']
#            newptdoc.last_name = form.cleaned_data['last_name']
#            newptdoc.save()
#            messages.add_message(request, messages.SUCCESS, "Added patient " + form.cleaned_data['first_name'] + " " + form.cleaned_data['last_name'])
#            return HttpResponseRedirect(reverse('shine_home'))
#        else:
#            messages.add_message(request, messages.ERROR, "Failed to add patient!")
#            context['patient_form'] = form
#    else:
#        context['patient_form'] = BasicPatientForm()
#    return render_to_response("patient/new_patient.html", context_instance=context)

@login_required
def list_cases(request):
    """
    Full case list
    """
    cases = CommCareCase.view("shinepatient/cases_by_patient_guid", include_docs=True).all()
    for case in cases:
        try:
            pat = BasePatient.get_typed_from_dict(BasePatient.get_db().get(case.patient_guid))
            case.patient_name = "%s %s" % (pat.first_name, pat.last_name)
        except ResourceNotFound:
            case.patient_name = None
    return render_to_response("shinepatient/case_list.html", {"cases": cases},
                              context_instance=RequestContext(request))

@login_required
def single_case(request, case_id):
    case = CommCareCase.get(case_id)
    image_actions = filter(lambda x: hasattr(x, 'image'), case.actions)

    thumbsize = int(request.GET.get('thumbsize', 400))
    crop = request.GET.get('crop','center')

    def mk_thumbnail(doc_id, k):
        try:
            attach = ImageAttachment.objects.get(xform_id=doc_id, attachment_key=k)
            im = get_thumbnail(attach.image, '%sx%s' % (thumbsize, thumbsize), crop=crop, quality=90)
            return im
        except ImageAttachment.DoesNotExist:
            logging.error("Error retrieving image attachment %s for submission %s" % (k,doc_id))
            return None
    image_action_dict = {}
    for ima in image_actions:
        #this assumes that a single submission can only have 1 image attachment!
        xform_id = ima['xform_id']
        filename = ima['image']['#text']
        thumbnail = mk_thumbnail(xform_id, filename)
        image_action_dict[ima] = [thumbnail]
    try:
        pat = BasePatient.get_typed_from_dict(BasePatient.get_db().get(case.patient_guid))
    except ResourceNotFound:
        pat = None
    return render_to_response("shinepatient/single_case.html",
                              {"patient": pat,
                               "case": case,
                               "json_case": json.dumps(case.to_json()),
                               "image_actions": image_action_dict,
                                },
                              context_instance=RequestContext(request))
    