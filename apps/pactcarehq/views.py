from patient.models.couchmodels import CPatient
import uuid
from django.http import HttpResponse, HttpResponseRedirect
from django_digest.decorators import httpdigest
from couchforms.views import post as couchforms_post
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from couchforms.util import post_xform_to_couch
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from couchforms.models import XFormInstance
from django.shortcuts import render_to_response
from pactcarehq.models import trial1mapping
from pactcarehq.forms.progress_note_comment import ProgressNoteComment
import logging
from django.core.urlresolvers import reverse
from datetime import datetime

def get_ghetto_registration_block(user):
    registration_block = """
    <registration>
                <username>%s</username>
                <password>%s</password>
                <uuid>%s</uuid>
                <date>%s</date>
                <registering_phone_id>%s</registering_phone_id>
                <user_data>
                    <data key="promoter_id">%s</data>
                    <data key="promoter_name">%s</data>
                    <data key="promoter_member_id">%s</data>
                </user_data>

           </registration>
           """
    #promoter_member_id is the nasty id from the csv, this should be fixed to match the Partners id -->
    resp_txt = ""
    #prov = Provider.objects.filter(user=user)[0] #hacky nasty
    return registration_block % (user.username, user.password, user.id, user.date_joined.strftime("%Y-%m-%dT%H:%M:%S.000"), uuid.uuid1().hex, user.id, user.username, "blah")

@require_POST
@csrf_exempt
def post(request):
    """
    Post an xform instance here.
    """
    try:
        #print request.FILES.keys()
        if request.FILES.has_key("xml_submission_file"):
            instance = request.FILES["xml_submission_file"].read()
            #print instance
            post_xform_to_couch(instance)
            resp = HttpResponse()
            resp.write("success")
            resp.status_code = 201
            return resp
        else:
            return HttpResponse("No form data")
    except Exception, e:
        return HttpResponse("fail")


@httpdigest()
def get_caselist(request):
    regblock= get_ghetto_registration_block(request.user)
    patient_block = ""
    patients = CPatient.view("patient/search", include_docs=True)
    for pt in patients:
        patient_block += pt.ghetto_xml()
    resp_text = "<restoredata>%s %s</restoredata>" % (regblock, patient_block)
    #logging.error(resp_text)

    response = HttpResponse(mimetype='text/xml')
    response.write(resp_text)
    return response


#@login_required
#def show_ghetto_patientlist(request, template_name="pactcarehq/ghetto_patient_list.html":
#    patients = CPatient.view("patient/by_last_name")
#    context = RequestContext(request)


@login_required
def show_submits_by_me(request, template_name="pactcarehq/ghetto_progress_submits.html"):
    context = RequestContext(request)
#    notes = XFormInstance
    notes_documents = XFormInstance.view("pactcarehq/all_progress_notes", key=request.user.username, include_docs=True).all()
    notes = []
    for note in notes_documents:
        case_id = note.form['case']['case_id']
        ############################################
        #hack to test the old ids
        try:
            oldpt = trial1mapping.objects.get(old_uuid=case_id)
            case_id = oldpt.get_new_patient_doc_id()
        except:
            print "can't find that patient/case: %s" % (case_id)
        #######################3

        patient = CPatient.view('patient/all', key=case_id, include_document=True).first()
        patient_name = patient.last_name
        notes.append([note._id,  note.form['Meta']['TimeEnd'], patient_name])

    context['progress_notes'] = notes
    return render_to_response(template_name, context_instance=context)

@login_required
def show_progress_note(request, doc_id, template_name="pactcarehq/view_progress_submit.html"):
    context = RequestContext(request)
    progress_note = XFormInstance.get(doc_id)['form']['note']


    context['times'] = progress_note['times']
    context['referrals'] = progress_note['referrals']
    context['bloodwork'] = progress_note['bwresults']
    context['memo'] = progress_note['memo']

    context['discussions'] =  {}
    context['discussions']['appointments'] = progress_note['discussed_appointments']
    context['discussions']['goals'] = progress_note['discussed_goals']
    context['discussions']['followup'] = progress_note['discussed_followup']
    context['discussions']['cd'] = progress_note['reviewed_cd']
    context['discussions']['qsp'] = progress_note['discussed_qsp']

    if request.method == 'POST':
            form = ProgressNoteComment(data=request.POST)
            context['form'] = form
            if form.is_valid():
                edit_comment = form.cleaned_data["comment"]
                return HttpResponseRedirect(reverse('manage-case', kwargs= {'case_id': case_id}))
    else:
        #it's a GET, get the default form
        if request.GET.has_key('comment'):
            context['form'] = ProgressNoteComment()
    return render_to_response(template_name, context_instance=context)




