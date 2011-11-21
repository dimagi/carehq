from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import logging
import isodate
from couchforms.models import XFormInstance
from couchforms.util import post_xform_to_couch
from pactcarehq.forms.progress_note_comment import ProgressNoteComment
from .util import form_xmlns_to_names, ms_from_timedelta
from pactcarehq.views.patient_views import _get_submissions_for_patient
from pactpatient.models.pactmodels import PactPatient
from patient.models.patientmodels import CSimpleComment, Patient

import uuid
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django import forms
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from couchexport.schema import get_docs


###################################################
# View file to view submissions by someone or for someone
# As well as receive submissions, but these are to be deprecated by the receiver app


def do_submission(instance, attachments={}):
    start_time = datetime.utcnow()
    doc = post_xform_to_couch(instance, attachments=attachments)
    delta_post =  datetime.utcnow() - start_time
    logging.debug("Submission posted: %d ms, doc_id: %s" % (ms_from_timedelta(delta_post), doc._id))



@require_POST
@csrf_exempt
def post(request):
    """
    Post an xform instance here.
    """
    try:
        if request.FILES.has_key("xml_submission_file"):
            attachments = {}
            instance = request.FILES["xml_submission_file"].read()
            for key, item in request.FILES.items():
                if key != "xml_submission_file":
                    attachments[key] = item

            #t = Thread(target=do_submission, args=(instance,))
            #t.start()

            #todo: need to switch this into using receiver
            do_submission(instance, attachments=attachments)

            resp = HttpResponse(status=201)
            #resp['Content-Length'] = 0 #required for nginx
            return resp
        else:
            logging.error("Error, no form data")
            return HttpResponse("No form data")
    except Exception, e:
        logging.error("Error on submission: %s" % (e))
        return HttpResponse("fail")


@login_required
def chw_submits(request, chw_username, template_name="pactcarehq/chw_submits.html"):
    context = RequestContext(request)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    submits = _get_submissions_for_user(chw_username)
    context['username'] = chw_username
    context['submit_arr'] = submits
    return render_to_response(template_name, context_instance=context)


@login_required
def all_submits_by_user(request, template_name="pactcarehq/submits_by_chw.html"):
    """A list of all xform submissions itemized by form type for ALL users"""
    context = RequestContext(request)
    submit_dict = {}
    for user in User.objects.all().filter(is_active=True):
        username = user.username
        #hack to skip the _ names
        if username.count("_") > 0:
            continue
        submit_dict[username] = _get_submissions_for_user(username)
    context['submit_dict'] = submit_dict
    return render_to_response(template_name, context_instance=context)

@login_required
def all_submits_by_patient(request, template_name="pactcarehq/submits_by_patient.html"):
    context = RequestContext(request)
    patient_list = []

    patients = Patient.objects.all()
    patients = sorted(patients, key=lambda x: x.couchdoc.last_name)
    for pt in patients:
        patient_list.append((pt,_get_submissions_for_patient(pt)))
    context['patient_list'] = patient_list
    return render_to_response(template_name, context_instance=context)



patient_case_id_cache = {}
def _get_submissions_for_user(username):
    """For a given username, return an array of submissions with an element [doc_id, date, patient_name, formtype]"""
    xform_submissions = XFormInstance.view("pactcarehq/all_submits", key=username, include_docs=True).all()
    submissions = []
    for xform in xform_submissions:
        if not xform.form.has_key('case'):
            continue
        if not xform.form['case'].has_key('case_id'):
            continue
        case_id = xform.form['case']['case_id']

        #for dev purposes this needs to be done for testing
        #case_id = _hack_get_old_caseid(case_id)
        if not patient_case_id_cache.has_key(case_id):
            patient = PactPatient.view('pactpatient/by_case_id', key=case_id, include_docs=True).first()
            patient_case_id_cache[case_id]= patient
        patient = patient_case_id_cache[case_id]

        if patient == None:
            patient_name = "Unknown"
        else:
            patient_name = patient.last_name

        xmlns = xform['xmlns']

        def stringify_delta(td):
            #where it's 0:07:06 H:M:S
            presplits = str(td).split(',')

            splits = presplits[-1].split(':')
            hours = int(splits[0])
            mins = int(splits[1])
            secs = float(splits[2])
            if secs > 30:
                mins+= 1
                secs = 0
            if mins > 30:
                hours += 1
                mins = 0
            newsplit = []
            days = False
            if len(presplits) == 2 and presplits[0] != "-1 day":
                #there's a day here
                newsplit.append(presplits[0])
                days=True

            if hours > 0:
                newsplit.append("%d hr" % (hours))
            if mins > 0 and days == False:
                newsplit.append("%d min" % (mins))
            return ', '.join(newsplit)


        started = xform.get_form['Meta']['TimeStart']
        if isinstance(started, unicode):
            started = isodate.parse_datetime("%sT%s" % (started.split(' ')[0], started.split(' ')[1]))


        ended = xform.get_form['Meta']['TimeEnd']
        if ended == '':
            #hack, touchforms doesn't seem to set a TimeEnd
            ended = xform.received_on
        if isinstance(ended, unicode):
            ended = isodate.parse_datetime("%sT%s" % (ended.split(' ')[0], ended.split(' ')[1]))

        start_end = stringify_delta(ended - started)
        received = xform['received_on']
        end_received = stringify_delta(received - ended)

        if xmlns == 'http://dev.commcarehq.org/pact/dots_form':
            formtype = "DOTS"
            submissions.append([xform._id, xform.form['encounter_date'], patient, formtype, started, start_end, end_received, received])
        elif xmlns == "http://dev.commcarehq.org/pact/progress_note":
            formtype = "Progress Note"
            submissions.append([xform._id, xform.form['note']['encounter_date'], patient, formtype,started, start_end, end_received, received])
        elif xmlns == "http://dev.commcarehq.org/pact/bloodwork":
            formtype = "Bloodwork"
            #TODO implement bloodwork view
#            submissions.append([xform._id, xform.form['case']['date_modified'].date(), patient_name, formtype,started, start_end, end_received, received])
        else:
            formtype = "Unknown"
            #submissions.append([xform._id, xform.form['Meta']['TimeEnd'], patient_name, formtype, started, start_end, end_received, received])
    submissions=sorted(submissions, key=lambda x: x[1])
    return submissions

@login_required
def my_submits(request, template_name="pactcarehq/submits_by_chw.html"):
    context = RequestContext(request)
#    submissions = XFormInstance
    username = request.user.username

    submit_dict = {}
    submissions = _get_submissions_for_user(username)
    submit_dict[username] = submissions
    context['submit_dict'] = submit_dict
    return render_to_response(template_name, context_instance=context)


@login_required
def show_submission(request, doc_id, template_name="pactcarehq/view_submission.html"):
    context = RequestContext(request)
    xform = XFormInstance.get(doc_id)
    form_data = xform['form']
    context['form_type'] = form_xmlns_to_names.get(xform.xmlns, "Unknown")
    context['xform'] = xform

    comment_docs = CSimpleComment.view('patient/all_comments', key=doc_id, include_docs=True).all()
    comment_arr = []
    for cdoc in comment_docs:
        if cdoc.deprecated:
            continue
        comment_arr.append([cdoc, cdoc.created])

    #comment handling
    comment_arr = sorted(comment_arr, key=lambda x: x[1], reverse=True)
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

