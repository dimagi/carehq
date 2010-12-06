from patient.models.couchmodels import CPatient, CSimpleComment,CDotWeeklySchedule, CPhone
from patient.models.djangomodels import Patient
from couchexport.export import export_excel
from django.http import   Http404
from StringIO import StringIO
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
from pactcarehq.forms.weekly_schedule_form import ScheduleForm
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
import hashlib
import simplejson
from django.views.decorators.cache import cache_page
from pactcarehq.forms.address_form import AddressForm
from pactcarehq.forms.phone_form import PhoneForm
from pactcarehq.forms.pactpatient_form import CPatientForm
from threading import Thread

DAYS_OF_WEEK = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday']

@login_required
def export_excel_file(request):
    """
    Download all data for a couchdbkit model
    """
    export_tag = request.GET.get("export_tag", "")
    if not export_tag:
        return HttpResponse("You must specify a model to download")
    tmp = StringIO()
    if export_excel(export_tag, tmp):
        response = HttpResponse(mimetype='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=%s.xls' % export_tag
        response.write(tmp.getvalue())
        tmp.close()
        return response
    else:
        return HttpResponse("Sorry, there was no data found for the tag '%s'." % export_tag)

@login_required
def patient_list(request, template_name="pactcarehq/patient_list.html"):
    """Return a list of all the patients in the system"""
    patients = Patient.objects.all()
    sorted_pts = sorted(patients, key=lambda p: p.couchdoc.last_name)
    context= RequestContext(request)
    context['patients'] = sorted_pts
    return render_to_response(template_name, context_instance=context)


@login_required
def patient_view(request, patient_id, template_name="pactcarehq/patient.html"):

    schedule_show = request.GET.get("schedule", "active")

    schedule_edit = request.GET.get("edit_schedule", False)
    address_edit = request.GET.get("edit_address", False)
    phone_edit = request.GET.get("edit_phone", False)
    patient_edit = request.GET.get('edit_patient', None)

    patient = Patient.objects.get(id=patient_id)
    context = RequestContext(request)
    context['patient']=patient
    context['pdoc']=patient.couchdoc
    context['schedule_show'] = schedule_show
    context['schedule_edit'] = schedule_edit
    context['phone_edit'] = phone_edit
    context['address_edit'] = address_edit
    context['patient_edit'] = patient_edit

    if address_edit:
        context['address_form'] = AddressForm()
    if schedule_edit:
        context['schedule_form'] = ScheduleForm()
    if phone_edit:
        context['phone_form'] = PhoneForm()
    if patient_edit:
        context['patient_form'] = CPatientForm(patient_edit, instance=patient.couchdoc)
        
    if request.method == 'POST':
        if schedule_edit:
            form = ScheduleForm(data=request.POST)
            if form.is_valid():
                sched = CDotWeeklySchedule()
                #print form.cleaned_data
                for day in DAYS_OF_WEEK:
                    if form.cleaned_data[day] != None:
                        setattr(sched, day, form.cleaned_data[day].username)
                sched.started=datetime.utcnow()
                sched.comment=form.cleaned_data['comment']
                sched.created_by = request.user.username
                sched.deprecated=False
                patient.couchdoc.set_schedule(sched)
                return HttpResponseRedirect(reverse('pactcarehq.views.patient_view', kwargs={'patient_id':patient_id}))
            else:
                context['schedule_form'] = form
        elif address_edit:
            form = AddressForm(data=request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.created_by = request.user.username
                patient.couchdoc.set_address(instance)
                patient.couchdoc.save()
                return HttpResponseRedirect(reverse('pactcarehq.views.patient_view', kwargs={'patient_id':patient_id}))
            else:
                context['address_form'] = form
        elif phone_edit:
            form = PhoneForm(data=request.POST)
            if form.is_valid():
                new_phone = CPhone()
                new_phone.description = form.cleaned_data['description']
                new_phone.number = form.cleaned_data['number']
                new_phone.notes = form.cleaned_data['notes']
                new_phone.created_by = request.user.username
                patient.couchdoc.phones.append(new_phone)
                patient.couchdoc.save()
                return HttpResponseRedirect(reverse('pactcarehq.views.patient_view', kwargs={'patient_id':patient_id}))
        elif patient_edit:
            form = CPatientForm(patient_edit, instance=patient.couchdoc, data=request.POST)
            if form.is_valid():
                instance = form.save(commit=True)
                return HttpResponseRedirect(reverse('pactcarehq.views.patient_view', kwargs={'patient_id':patient_id}))


    return render_to_response(template_name, context_instance=context)




@login_required
def user_submit_tallies(request,template_name="pactcarehq/user_submits_report.html"):
    context = RequestContext(request)
    users = User.objects.all().filter(is_active=True)
    enddate = datetime.utcnow() - timedelta(days=0)
    timeval = timedelta(days=1)
    eval_date = enddate
    total_interval = 14
    if request.GET.has_key('interval'):
        try:
            total_interval = int(request.GET['interval'])
        except:
            pass


    schemas = ['http://dev.commcarehq.org/pact/progress_note', "http://dev.commcarehq.org/pact/dots_form"]
    submission_dict = {}
    datestrings = []
    for offset in range(0,total_interval):
        eval_date = enddate - timedelta(days=offset)
        datestrings.append(eval_date.strftime("%m/%d/%Y"))
    datestrings.reverse()
        
    for schema in schemas:
        submission_dict[schema] = {}
        for user in users:
            if user.username.count('_') > 0:
                continue
            submission_dict[schema][user.username] = []
            for offset in range(0,total_interval):
                eval_date = enddate - timedelta(days=offset)
                datestring = eval_date.strftime("%m/%d/%Y")

                #hack the view is doing zero indexed months
                startkey = [str(user.username),  eval_date.year, eval_date.month-1, eval_date.day, schema]
                #endkey = [str(user.username),  enddate.year, enddate.month, enddate.day, schema,{}]

                reduction = XFormInstance.view('pactcarehq/submits_by_user', key=startkey).all()
                if len(reduction) > 0:
                    submission_dict[schema][user.username].append(reduction[0]['value'])
                else:
                    submission_dict[schema][user.username].append(0)
            #when done let's reverse it so it goes from oldest to youngest left to right
            submission_dict[schema][user.username].reverse()

    context['user_submissions'] = submission_dict
    context['interval'] = total_interval
    context['datestrings'] = datestrings
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
            print "read file"
            t = Thread(target=threaded_submission, args=(instance,))
            t.start()
            resp = HttpResponse(status=201)
            resp['Content-Length'] = 0
            #resp.write("success")
            #resp.status_code = 203
            return resp
        else:
            return HttpResponse("No form data")
    except Exception, e:
        print "Error: %s" % (e)
        return HttpResponse("fail")


def threaded_submission(instance):
    doc = post_xform_to_couch(instance)
    print "posted"
    xform_saved.send(sender="post", form=doc) #ghetto way of signalling a submission signal
    print "post_signal: %s" % (doc)

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
@cache_page(60 * 5)
def patient_schedule_report(request, patient_id, template_name="pactcarehq/patient_calendar_submit_report.html"):
    """returns a view of the patient's scheduled visits for a given date (which chw it should have been), as well as the visit if there was one
    returns an acheduled_item, ...], [submissions], ...]
    """
    context = RequestContext(request)
    pt = Patient.objects.get(id=patient_id)

    date_range = 30

    ret = []
    context['patient'] = pt

    visit_dates = []
    scheduled_by_date = {}
    for n in range(0, date_range):
        td = timedelta(days=n)
        visit_date = datetime.utcnow()-td
        visit_dates.append(visit_date)

    submits_per_date = _get_submissions_for_patient_by_date(pt, visit_dates)
    for visit_date in visit_dates:
        if submits_per_date.has_key(visit_date):
            submits = submits_per_date[visit_date]
        else:
            submits = []
        #scheduled = scheduled_by_date[visit_date]
        scheduled_chw = _get_scheduled_chw_for_patient_visit(pt, visit_date)
        ret.append([visit_date, [scheduled_chw], submits])
    context['date_arr'] = ret
    return render_to_response(template_name, context_instance=context)





@login_required
def chw_submit_report(request, username, template_name="pactcarehq/chw_calendar_submit_report.html"):
    """Calendar view of submissions by CHW, overlaid with their scheduled visits, and whether they made them or not."""
    #note, as of this writing 11/29/2010 - it's a rather inefficient query doing it by patient by day - there ought to be a more efficient set of bulk queries that can do this
    context = RequestContext(request)
    all_patients = request.GET.get("all_patients", False)

    context['username'] = username


    try:
        user = User.objects.get(username=username)
        if all_patients == False:
            #do a filter for only the patients this CHW knows about
            condensed_schedules = CPatient.view('pactcarehq/chw_dot_scheduled_pact_ids', key=username).first()
            if condensed_schedules != None and condensed_schedules['value'] != None:
                known_pact_ids = condensed_schedules['value']
            else:
                known_pact_ids = []


        if all_patients == False and known_pact_ids:
            patients_temp = Patient.objects.all()
            patients = []
            for pt in patients_temp:
                if known_pact_ids.count(pt.couchdoc.pact_id) > 0:
                    patients.append(pt)
        else:
            patients = Patient.objects.all()
        date_range = 10
        ret = [] # date: (scheduled [patient, patient], submits[]) #match up by patient later

        visit_dates = []
        for n in range(0, date_range):
            td = timedelta(days=n)
            visit_date = datetime.utcnow()-td
            visit_dates.append(visit_date)

        pt_submission_map = {}
        #t = datetime.now()



        #load all the submissions for the given date range
        for pt in patients:
            #t2 = datetime.now()
            submits_per_date = _get_submissions_for_patient_by_date(pt, visit_dates)
            pt_submission_map[pt] = submits_per_date
            #d2 = datetime.now()-t2
            #print "\tSingle Patient data query: %d.%d" % (d2.seconds, d2.microseconds/1000)

        #d = datetime.now()-t
        #print "All Patient data query: %d.%d" % (d.seconds, d.microseconds/1000)

        #now, iterate through all each dates, check the scheduled chw to see if it matches and add patient as chw's "todo"
        for visit_date in visit_dates:
            submits_for_day = []
            scheduled_patients = []
            for pt in patients:
                #first, get the sheduled chw for this date
                scheduled_chw = _get_scheduled_chw_for_patient_visit(pt, visit_date)
                if scheduled_chw == username:
                    scheduled_patients.append(pt)

                #next get the submissions for that visit date and add it to the growing list
                if pt_submission_map[pt].has_key(visit_date):
                    submits = pt_submission_map[pt][visit_date]
                else:
                    submits = []
                submits_for_day.extend(submits)
            scheduled_patients = sorted(scheduled_patients, key=lambda x:x.couchdoc.last_name)
            ret.append([visit_date, scheduled_patients, submits_for_day])

        context['date_arr'] = ret
        return render_to_response(template_name, context_instance=context)

    except ObjectDoesNotExist, e:
        print e
        raise Http404



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

def _hack_get_old_caseid(new_case_id):
    #hack to test the old ids
    try:
        oldpt = trial1mapping.objects.get(old_uuid=new_case_id)
        old_case_id = oldpt.get_new_patient_doc_id()
    except:
        old_case_id=None
        print "can't find that patient/case: %s" % (new_case_id)
    return old_case_id


def _get_scheduled_chw_for_patient_visit(patient, visit_date):

    """Get the active scheduled chw for that day.
    returns a string of the chw username"""
    key = patient.couchdoc.pact_id
    visit_schedule_cache_key = hashlib.md5('patient_visit_schedule-%s-%s' % (key, visit_date.strftime("%Y-%m-%d"))).hexdigest()

    ####
    #Step 1, see if this has been cached before for that given chw
    chw_scheduled = cache.get(visit_schedule_cache_key, None)
    if chw_scheduled != None:
        #print "cache hit! %s on %s-%s" % (chw_scheduled, key, visit_date.strftime("%Y-%m-%d"))
        return chw_scheduled

    ################################
    #Step 2, get the patient's entire visit schedule, cache the whole thing

    pt_schedule_cache_key = 'patient_schedule_key-%s' % (patient.couchdoc.pact_id)
    sched_dicts = cache.get(pt_schedule_cache_key, None)
    if sched_dicts == None:
        reduction = CDotWeeklySchedule.view('pactcarehq/patient_dots_schedule', key=key).first()
        if reduction == None:
            cache.set(pt_schedule_cache_key, repr({}))
            sched_dicts = {}
        else:
            sched_dicts = reduction['value']
        sched_dicts = sorted(sched_dicts, key=lambda x: x['started'])

        cache.set(pt_schedule_cache_key, simplejson.dumps(sched_dicts))
    else:
        sched_dicts = simplejson.loads(sched_dicts)

    ######
    #Step 3
    #having received the schedule dictionary, now process the scheduled chw for that visit date
    used_schedule=None
    chw_scheduled = None
    day_of_week = visit_date.isoweekday() %7 #isoweekday is monday 1, sunday 7, mod 7 to make sunday 0
    for sched_dict in sched_dicts:
        sched = CDotWeeklySchedule.wrap(sched_dict)
        if (sched.ended == None or sched.ended > visit_date) and sched.started <= visit_date:
            used_schedule=sched
    if used_schedule != None:
        day_string = DAYS_OF_WEEK[day_of_week]
        chw_scheduled = used_schedule[day_string]
    cache.set(visit_schedule_cache_key, str(chw_scheduled))
    #print "setting cache: %s for %s-%s" %(chw_scheduled, key, visit_date.strftime("%Y-%m-%d"))
    
    return chw_scheduled

def _get_submissions_for_patient_by_date(patient, visit_dates, schema='http://dev.commcarehq.org/pact/dots_form'):
    """Argument: Patient django object, visit date
    Will return a view result of all submissions by patient where the key is the patient pact_id
    return value: [pact_id, year, month, day]=>submission"""

    keys = []
    date_key_map = {}
    #t2 = datetime.now()
    for visit_date in visit_dates:
        day_of_week = visit_date.isoweekday()-1
        yearstart = visit_date.year
        monthstart = visit_date.month
        datestart = visit_date.day
        #get the xform count for that day
        key = [patient.couchdoc.pact_id, yearstart, monthstart, datestart, schema]
        keys.append(key)
        key_str = ''.join([str(x) for x in key])
        date_key_map[key_str] = visit_date
    submit_reduction = XFormInstance.view('pactcarehq/all_submits_by_patient_date', keys=keys, group=True)
    #d2 = datetime.now()-t2
    #print "\tSingle Patient data query QUERY: %d.%d" % (d2.seconds, d2.microseconds/1000)
    #t3 = datetime.now()
    ret = {} #a return value of date ordered submissions by
    for row in submit_reduction:
        key = row['key']
        key_str = ''.join([str(x) for x in key])
        submits = row['value']

        date = date_key_map[key_str]
        ret[date] = [XFormInstance.wrap(x) for x in submits]
    #d3 = datetime.now()-t3

    #print "\tSingle Patient data query HASHING: %d.%d" % (d3.seconds, d3.microseconds/1000)

    return ret





def _get_submissions_for_patient(patient):
    """Returns a view of all the patients submissions by the patient's case_id (which is their CPatient doc_id, this probably should be altered)
    """
    xform_submissions = XFormInstance.view('pactcarehq/all_submits_by_case', key=patient.doc_id)
    submissions = []
    for note in xform_submissions:
        if not note.form.has_key('case'):
            continue
        xmlns = note['xmlns']
        if xmlns == 'http://dev.commcarehq.org/pact/dots_form':
            formtype = "DOTS"
        elif xmlns == "http://dev.commcarehq.org/pact/progress_note":
            formtype = "Progress Note"
        else:
            formtype = "Unknown"
        submissions.append([note._id, note.form['Meta']['TimeEnd'], note.form['Meta']['username'] , formtype])
    submissions=sorted(submissions, key=lambda x: x[1])
    return submissions



def _get_submissions_for_user(username):
    """For a given username, return an array of submissions with an element [doc_id, date, patient_name, formtype]"""
    xform_submissions = XFormInstance.view("pactcarehq/all_submits", key=username, include_docs=True).all()
    submissions = []
    for xform in xform_submissions:
        if not xform.form.has_key('case'):
            continue
        case_id = xform.form['case']['case_id']

        #for dev purposes this needs to be done for testing
        #case_id = _hack_get_old_caseid(case_id)
        patient = CPatient.view('patient/all', key=case_id, include_document=True).first()
        if patient == None:
            patient_name = "Unknown"
        else:
            patient_name = patient.last_name

        xmlns = xform['xmlns']
        if xmlns == 'http://dev.commcarehq.org/pact/dots_form':
            formtype = "DOTS"
        elif xmlns == "http://dev.commcarehq.org/pact/progress_note":
            formtype = "Progress Note"
        else:
            formtype = "Unknown"
        submissions.append([xform._id, xform.form['Meta']['TimeEnd'], patient_name, formtype])
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
def show_progress_note(request, doc_id, template_name="pactcarehq/view_progress_submit.html"):
    context = RequestContext(request)
    xform = XFormInstance.get(doc_id)
    progress_note = xform['form']['note']
    context['progress_note'] = progress_note

    case_id = xform['form']['case']['case_id']



    ###########################################################
    #for dev purposes this needs to be done for testing
    #but this is important still tog et the patient info for display
    #case_id = _hack_get_old_caseid(case_id)
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
    #case_id = _hack_get_old_caseid(case_id)
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
                return HttpResponseRedirect(request.path)
    else:
        #it's a GET, get the default form
        if request.GET.has_key('comment'):
            context['form'] = ProgressNoteComment()
    return render_to_response(template_name, context_instance=context)






