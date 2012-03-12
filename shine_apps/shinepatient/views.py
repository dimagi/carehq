# To manage patient views for create/view/update you need to implement them directly in your patient app
from _collections import defaultdict
from datetime import datetime
import hashlib
import logging
import tempfile
import uuid
import re
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from sorl.thumbnail.shortcuts import get_thumbnail
from clinical_core.webentry.util import get_remote_form, user_meta_preloaders, shared_preloaders
from couchforms.models import XFormInstance
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from hutch.models import  AttachmentImage, AuxMedia
from patient.models import BasePatient
from receiver.util import spoof_submission
from shinepatient.forms import  ClinicalImageUploadForm
from casexml.apps.case.models import CommCareCase
import json
from couchdbkit.resource import ResourceNotFound
from patient.views import  PatientSingleView
from touchforms.formplayer.views import play_remote, get_remote_instance


class MepiPatientSingleView(PatientSingleView):
    patient_list_url = '/' #hardcoded from urls, because you can't do a reverse due to the urls not being bootstrapped yet.

    def get_context_data(self, **kwargs):
        """
        Main patient view for pact.  This is a "do lots in one view" thing that probably shouldn't be replicated in future iterations.
        """

        request = self.request
        patient_guid = self.kwargs['patient_guid']
        patient_edit = request.GET.get('edit_patient', None)

        #global info
        view_mode = self.kwargs.get('view_mode', '')
        if view_mode == '':
            view_mode = 'info'
        context = super(MepiPatientSingleView, self).get_context_data(**kwargs)
        context['view_mode'] = view_mode
        pdoc = context['patient_doc']
        dj_patient = context['patient_django']
#        context['patient_list_url'] = reverse('my_patients')
        context['patient_edit'] = patient_edit
        if patient_edit:
            context['patient_form'] = SimplePatientForm(patient_edit, instance=pdoc)



        if view_mode == 'info':
            self.template_name = "shinepatient/shinepatient_info.html"

        if view_mode == 'files':
            self.template_name = "shinepatient/shinepatient_files.html"

        if view_mode == 'data':
            self.template_name = "shinepatient/shinepatient_data.html"

        if view_mode == 'submissions':
            submissions = [XFormInstance.get(x) for x in pdoc.latest_case.xform_ids]
            context['submissions'] = submissions
            self.template_name = "shinepatient/shinepatient_submissions.html"

        if view_mode == 'logs':
            logs = ''

        return context
        #return render_to_response(template_name, context_instance=context)


@login_required
def upload_patient_photo(request, patient_guid, template_name='shinepatient/upload_photo.html'):
    context = RequestContext(request)
    patient = BasePatient.get_typed_from_dict(BasePatient.get_db().get(patient_guid))

    def handle_uploaded_file(f, form):
        destination = tempfile.NamedTemporaryFile()
        checksum = hashlib.md5()
        for chunk in f.chunks():
            checksum.update(chunk)
            destination.write(chunk)
        destination.seek(0)
        image_type = form.cleaned_data['image_type'],
        media_meta=dict(image_type=image_type[0])

        attachment_id = uuid.uuid4().hex
        new_image_aux = AuxMedia(uploaded_date=datetime.utcnow(),
                             uploaded_by=request.user.username,
                             uploaded_filename=f.name,
                             checksum=checksum.hexdigest(),
                             attachment_id=attachment_id,
                             media_meta=media_meta,
                             notes=form.cleaned_data['notes'])
        patient.put_attachment(destination, attachment_id, content_type=f.content_type, content_length=f.size)
        destination.close()
        return new_image_aux

    if request.method == 'POST':
        form = ClinicalImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = handle_uploaded_file(request.FILES['image_file'], form)
            patient['aux_media'].append(image)
            patient.save()
            return HttpResponseRedirect(reverse('shine_single_patient', kwargs={'patient_guid': patient_guid}))
    else:
        form = ClinicalImageUploadForm()
    context['form'] = form
    context['patient_guid'] = patient_guid
    return render_to_response(template_name, context)



@login_required
def new_patient_touch(request):
    preloaders = shared_preloaders()
    preloaders.update(user_meta_preloaders(request.user))
    playsettings = defaultdict(lambda: "")
    playsettings["xform"] = get_remote_form("https://bitbucket.org/ctsims/commcare-sets/raw/tip/shine/patient_registration.xml")
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
            attach = AttachmentImage.objects.get(xform_id=doc_id, attachment_key=k)
            im = get_thumbnail(attach.image, '%sx%s' % (thumbsize, thumbsize), crop=crop, quality=90)
            return im
        except AttachmentImage.DoesNotExist:
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
    