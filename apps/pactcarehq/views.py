from patient.models.couchmodels import CPatient, CSimpleComment
import uuid
from django.http import HttpResponse, HttpResponseRedirect
from django_digest.decorators import httpdigest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from couchforms.util import post_xform_to_couch
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from couchforms.models import XFormInstance
from django.shortcuts import render_to_response
from pactcarehq.models import trial1mapping
from pactcarehq.forms.progress_note_comment import ProgressNoteComment
from django.core.urlresolvers import reverse
from couchforms.signals import xform_saved
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import logging


@login_required
def dashboard(request,template_name="pactcarehq/user_submits_report.html"):
    context = RequestContext(request)
    users = User.objects.all().filter(is_active=True)
    enddate = datetime.utcnow() - timedelta(days=80)
    timeval = timedelta(days=1)
    eval_date = enddate

    total_interval = 7

    schemas = ['http://dev.commcarehq.org/pact/progress_note', "http://dev.commcarehq.org/pact/dots_form"]
    submission_dict = {}
    for schema in schemas:
        submission_dict[schema] = {}
        for user in users:
            if user.username.count('_') > 0:
                continue
            submission_dict[schema][user.username] = {}
            for offset in range(0,total_interval):
                eval_date = enddate - timedelta(days=offset)
                datestring = eval_date.strftime("%m/%d/%Y")

                startkey = [str(user.username),  eval_date.year, eval_date.month, eval_date.day, schema]
                #endkey = [str(user.username),  enddate.year, enddate.month, enddate.day, schema,{}]

                reduction = XFormInstance.view('pactcarehq/submits_by_user', key=startkey).all()
                if len(reduction) > 0:
                    submission_dict[schema][user.username][datestring] = reduction[0]['value']
                else:
                    submission_dict[schema][user.username][datestring] = 0

    context['user_submissions'] = submission_dict
    return render_to_response(template_name, context_instance=context)


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
            doc = post_xform_to_couch(instance)
            print "posted"
            xform_saved.send(sender="post", form=doc) #ghetto way of signalling a submission signal
            print "post_signal: %s" % (doc)
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
def all_submits(request, template_name="pactcarehq/ghetto_progress_submits.html"):
    context = RequestContext(request)
    submit_dict = {}
    for user in User.objects.all():
        username = user.username
        #hack to skip the _ names
        if username.count("_") > 0:
            continue
        submit_dict[username] = _get_submissions_for_user(username)
    context['submit_dict'] = submit_dict
    return render_to_response(template_name, context_instance=context)


def _hack_get_old_caseid(new_case_id):
    #hack to test the old ids
    try:
        oldpt = trial1mapping.objects.get(old_uuid=new_case_id)
        old_case_id = oldpt.get_new_patient_doc_id()
    except:
        old_case_id=None
        print "can't find that patient/case: %s" % (new_case_id)
    return old_case_id


def _sort_arr_by_date(a,b):
    return cmp(a[1],b[1])

def _sort_arr_by_date_desc(a,b):
    return cmp(b[1],a[1])

def _get_submissions_for_user(username):
    notes_documents = XFormInstance.view("pactcarehq/all_submits", key=username, include_docs=True).all()
    submissions = []
    for note in notes_documents:
        if not note.form.has_key('case'):
            continue
        case_id = note.form['case']['case_id']

        #for dev purposes this needs to be done for testing
        case_id = _hack_get_old_caseid(case_id)

        patient = CPatient.view('patient/all', key=case_id, include_document=True).first()
        if patient == None:
            patient_name = "Unknown"
        else:
            patient_name = patient.last_name

        xmlns = note['xmlns']
        if xmlns == 'http://dev.commcarehq.org/pact/dots_form':
            formtype = "DOTS"
        elif xmlns == "http://dev.commcarehq.org/pact/progress_note":
            formtype = "Progress Note"
        else:
            formtype = "Unknown"
        submissions.append([note._id, note.form['Meta']['TimeEnd'], patient_name, formtype])
    submissions.sort(_sort_arr_by_date)
    return submissions

@login_required
def my_submits(request, template_name="pactcarehq/ghetto_progress_submits.html"):
    context = RequestContext(request)
#    submissions = XFormInstance
    username = request.user.username

    submit_dict = {}
    submissions = _get_submissions_for_user(username)
    submit_dict[username] = submissions
    context['submit_dict'] = submit_dict
    return render_to_response(template_name, context_instance=context)

@login_required
def show_progress_note(request, doc_id, template_name="pactcarehq/view_progress_submit.html"):
    context = RequestContext(request)
    xform = XFormInstance.get(doc_id)
    progress_note = xform['form']['note']
    context['progress_note'] = progress_note

    case_id = xform['form']['case']['case_id']



    ###########################################################
    #for dev purposes this needs to be done for testing
    #but this is important still tog et the patient info for display
    case_id = _hack_get_old_caseid(case_id)
    patient = CPatient.view('patient/all', key=case_id, include_document=True).first()
    if patient == None:
        patient_name = "Unknown"
    else:
        patient_name = patient.first_name + " " + patient.last_name
    context['patient_name'] = patient_name
    ##############################################################



    comment_docs = CSimpleComment.view('patient/all_comments', key=doc_id).all()
    comment_arr = []
    for cdoc in comment_docs:
        if cdoc.deprecated:
            continue
        comment_arr.append([cdoc, cdoc.created])

    comment_arr.sort(_sort_arr_by_date_desc)
    context['comments'] = comment_arr

    if request.method == 'POST':
            form = ProgressNoteComment(data=request.POST)
            context['form'] = form
            if form.is_valid():
                edit_comment = form.cleaned_data["comment"]
                ccomment = CSimpleComment()
                ccomment.doc_fk_id = doc_id
                ccomment.comment = edit_comment
                ccomment.created_by = request.user.username
                ccomment.created = datetime.utcnow()
                ccomment.save()
                return HttpResponseRedirect(reverse('show_progress_note', kwargs= {'doc_id': doc_id}))
    else:
        #it's a GET, get the default form
        if request.GET.has_key('comment'):
            context['form'] = ProgressNoteComment()
    return render_to_response(template_name, context_instance=context)


@login_required
def show_dots_note(request, doc_id, template_name="pactcarehq/view_dots_submit.html"):
    context = RequestContext(request)
    xform = XFormInstance.get(doc_id)
    dots_note = {}
    raw = xform['form']
    dots_note['encounter_date'] = raw['encounter_date']
    dots_note['schedued'] = raw['scheduled']
    dots_note['visit_type'] = raw['visit_type']
    dots_note['visit_kept'] = raw['visit_kept']
    dots_note['contact_type'] = raw['contact_type']
    dots_note['observed_art'] = raw['observed_art']
    try:
        dots_note['observed_art_dose'] = raw['observed_art_dose']
        dots_note['observed_non_art_dose'] = raw['observed_non_art_dose']
    except:
        logging.error("Error, missing keys: observed_art_dose and observed_non_art_dose")
    dots_note['observed_non_art'] = raw['observed_non_art']
    dots_note['notes'] = raw['notes']



    context['dots_note'] = dots_note
    case_id = xform['form']['case']['case_id']

    ###########################################################
    #for dev purposes this needs to be done for testing
    #but this is important still tog et the patient info for display
    case_id = _hack_get_old_caseid(case_id)
    patient = CPatient.view('patient/all', key=case_id, include_document=True).first()
    if patient == None:
        patient_name = "Unknown"
    else:
        patient_name = patient.first_name + " " + patient.last_name
    context['patient_name'] = patient_name
    ##############################################################



    comment_docs = CSimpleComment.view('patient/all_comments', key=doc_id).all()
    comment_arr = []
    for cdoc in comment_docs:
        if cdoc.deprecated:
            continue
        comment_arr.append([cdoc, cdoc.created])

    comment_arr.sort(_sort_arr_by_date_desc)
    context['comments'] = comment_arr

    if request.method == 'POST':
            form = ProgressNoteComment(data=request.POST)
            context['form'] = form
            if form.is_valid():
                edit_comment = form.cleaned_data["comment"]
                ccomment = CSimpleComment()
                ccomment.doc_fk_id = doc_id
                ccomment.comment = edit_comment
                ccomment.created_by = request.user.username
                ccomment.created = datetime.utcnow()
                ccomment.save()
                return HttpResponseRedirect(request.path)
    else:
        #it's a GET, get the default form
        if request.GET.has_key('comment'):
            context['form'] = ProgressNoteComment()
    return render_to_response(template_name, context_instance=context)






