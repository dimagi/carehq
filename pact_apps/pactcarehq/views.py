import urllib
from couchdbkit.exceptions import ResourceNotFound
from django import forms
from django.core.servers.basehttp import FileWrapper
from casexml.apps.case.models import CommCareCase
from couchexport.schema import get_docs
from dimagi.utils.couch.database import get_db
from pactpatient.forms import PactPatientEditForm
from pactpatient.forms import PhoneForm, AddressForm, SimpleAddressForm
from pactpatient.models import PactPatient, CDotWeeklySchedule
from pactpatient.models import CActivityDashboard
from patient.models import CAddress, CPhone, CSimpleComment
from patient.models import Patient
from django.http import   Http404
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
from django.contrib.auth.models import User
from datetime import datetime, timedelta, time
import logging
from pactcarehq.forms.weekly_schedule_form import ScheduleForm
from django.core.cache import cache
import hashlib
import simplejson
from django.views.decorators.cache import cache_page
from pactcarehq import schedule
from pactcarehq.tasks import all_chw_submit_report, schema_export
import tempfile
from django import forms

DAYS_OF_WEEK = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday']

@login_required
def export_excel_file(request):
    """
    Download all data for a couchdbkit model
    """

    namespace = request.GET.get("export_tag", "")
    if not namespace:
        return HttpResponse("You must specify a model to download")
    docs = get_docs(namespace)
    if not docs:
        return HttpResponse("Error, no documents for that schema exist")
    download_id = uuid.uuid4().hex
    schema_export.delay(namespace, download_id)
    return HttpResponseRedirect(reverse('downloader.downloaderviews.retrieve', kwargs={'download_id': download_id}))

@login_required()
def export_landing(request, template_name="pactcarehq/export_landing.html"):

    class RequestDownloadForm(forms.Form):
        email_address = forms.CharField(error_messages = {'required':
                                                'You must enter an email'})

    context = RequestContext(request)
    if request.method == "POST":
        form = RequestDownloadForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['email_address']
            download_id = uuid.uuid4().hex
            namespace = "http://dev.commcarehq.org/pact/progress_note"
            context['email'] = email
            context['download_id'] = download_id

            schema_export.delay(namespace, download_id, email=email)

        else:
            context['form'] = form
    else:
        context['form'] = RequestDownloadForm()

    return render_to_response(template_name, context_instance=context)


    

@login_required
def patient_list(request, template_name="pactcarehq/patient_list.html"):
    """Return a list of all the patients in the system"""
    patients = Patient.objects.all()
    sorted_pts = sorted(patients, key=lambda p: p.couchdoc.last_name)

    #if there's a mismatch of the patients in django and in couch (eg dev environment)
    #patients = filter(lambda x: x.couchdoc !=None, patients)
    #sorted_pts = sorted(patients, key=lambda p: p.couchdoc.last_name)

    context= RequestContext(request)
    context['patients'] = sorted_pts
    return render_to_response(template_name, context_instance=context)


@login_required
def remove_schedule(request):
    if request.method == "POST":
        try:
            patient_id = urllib.unquote(request.POST['patient_id']).encode('ascii', 'ignore')
            patient = Patient.objects.get(id=patient_id)
            schedule_id = urllib.unquote(request.POST['schedule_id']).encode('ascii', 'ignore')
            remove_id = -1
            for i in range(0, len(patient.couchdoc.weekly_schedule)):
                sched = patient.couchdoc.weekly_schedule[i]
                if sched.schedule_id == schedule_id:
                    remove_id = i
                    break

            new_schedules = []
            couchdoc = patient.couchdoc
            if remove_id != -1:
                #note the idiocy of me needing to iterate through the list in order to delete it.
                #a simple remove() or a pop(i) could not work for some reason
                for i in range(0, len(couchdoc.weekly_schedule)):
                    if i == remove_id:
                        continue
                    new_schedules.append(couchdoc.weekly_schedule[i])

                couchdoc.weekly_schedule = new_schedules
                couchdoc.save()
            return HttpResponseRedirect(reverse('pactcarehq.views.patient_view', kwargs={'patient_id':patient_id}))
        except Exception, e:
            logging.error("Error getting args:" + str(e))
            return HttpResponse("Error: %s" % (e))
    else:
        pass


@login_required
def patient_view(request, patient_id, template_name="pactcarehq/patient.html"):
    """
    Main patient view for pact.  This is a "do lots in one view" thing that probably shouldn't be replicated in future iterations.
    """

    schedule_show = request.GET.get("schedule", "active")
    schedule_edit = request.GET.get("edit_schedule", False)
    address_edit = request.GET.get("edit_address", False)
    address_edit_id = request.GET.get("address_id", None)
    new_address = True if request.GET.get("new_address", False) == "True" else False
    phone_edit = request.GET.get("edit_phone", False)
    patient_edit = request.GET.get('edit_patient', None)
    show_all_schedule = request.GET.get('allschedules', None)


    patient = Patient.objects.get(id=patient_id)
    context = RequestContext(request)
    context['patient']=patient
    context['pdoc']=patient.couchdoc
    context['schedule_show'] = schedule_show
    context['schedule_edit'] = schedule_edit
    context['phone_edit'] = phone_edit
    context['address_edit'] = address_edit
    context['patient_edit'] = patient_edit
    context['submit_arr'] = _get_submissions_for_patient(patient)
    context['casedoc'] = CommCareCase.get(patient.couchdoc.case_id)

    last_bw = patient.couchdoc.last_bloodwork
    context['last_bloodwork'] = last_bw



    if last_bw == None:
        context['bloodwork_missing']  = True
    else:
        context['since_bw'] = (datetime.utcnow() - last_bw.get_date).days

        if (datetime.utcnow() - last_bw.get_date).days > 90:
            context['bloodwork_overdue'] = True
        else:
            context['bloodwork_overdue'] = False


    if address_edit and not new_address:
        if len(patient.couchdoc.address) > 0:
            #if there's an existing address out there, then use it, else, make a new one
            context['address_form'] = SimpleAddressForm(instance=patient.couchdoc.get_address(address_edit_id))
        else:
            context['address_form'] = SimpleAddressForm()
    if new_address:
        context['address_form'] = SimpleAddressForm()
        context['address_edit'] = True
    if schedule_edit:
        context['schedule_form'] = ScheduleForm()
    if phone_edit:
        context['phone_form'] = PhoneForm()
    if patient_edit:
        context['patient_form'] = PactPatientEditForm(patient_edit, instance=patient.couchdoc)
    if show_all_schedule != None:
        context['past_schedules'] = patient.couchdoc.past_schedules
        
    if request.method == 'POST':
        if schedule_edit:
            form = ScheduleForm(data=request.POST)
            if form.is_valid():
                sched = CDotWeeklySchedule()
                for day in DAYS_OF_WEEK:
                    if form.cleaned_data[day] != None:
                        setattr(sched, day, form.cleaned_data[day].username)
                if form.cleaned_data['active_date'] == None:
                    sched.started=datetime.utcnow()
                else:
                    sched.started = datetime.combine(form.cleaned_data['active_date'], time.min)
                sched.comment=form.cleaned_data['comment']
                sched.created_by = request.user.username
                sched.deprecated=False
                patient.couchdoc.set_schedule(sched)
                return HttpResponseRedirect(reverse('pactcarehq.views.patient_view', kwargs={'patient_id':patient_id}))
            else:
                context['schedule_form'] = form
        elif address_edit or new_address:
            form = SimpleAddressForm(data=request.POST)
            if form.is_valid():
                is_new_addr = False
                if form.cleaned_data['address_id'] != '':
                    is_new_addr=False
                    address_edit_id = form.cleaned_data['address_id']
                    instance = patient.couchdoc.get_address(address_edit_id)
                else:
                    is_new_addr=True
                    instance=CAddress()
                    instance.created_by = request.user.username
                instance.description = form.cleaned_data['description']
                instance.full_address = form.cleaned_data['address']

                if is_new_addr == False:
                    index = patient.couchdoc.address_index(address_edit_id)
                    patient.couchdoc.address[index] = instance
                else:
                    patient.couchdoc.set_address(instance)

                #patient.couchdoc.save()
                #do patient xml submit
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
            else:
                logging.error("Error, invalid phone form data")
        elif patient_edit:
            form = PactPatientEditForm(patient_edit, instance=patient.couchdoc, data=request.POST)
            if form.is_valid():
                instance = form.save(commit=True)
                return HttpResponseRedirect(reverse('pactcarehq.views.patient_view', kwargs={'patient_id':patient_id}))


    return render_to_response(template_name, context_instance=context)

def get_ghetto_registration_block(user):
    registration_block = """
    <Registration xmlns="http://openrosa.org/user/registration">
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
   </Registration>
   """
    #promoter_member_id is the nasty id from the csv, this should be fixed to match the Partners id -->
    resp_txt = ""
    #prov = Provider.objects.filter(user=user)[0] #hacky nasty
    return registration_block % (user.username, user.password, user.id, user.date_joined.strftime("%Y-%m-%dT%H:%M:%S.000"), uuid.uuid4().hex, user.id, user.username, "blah")

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
def my_patient_activity_grouped(request, template_name="pactcarehq/patients_dashboard.html"):
    """Return a list of all the patients in the system"""
    #using per patient instance lookup...slow, but reuasable
    context= RequestContext(request)

    if request.user.is_superuser == True:
        #patients = Patient.objects.all()
        assignments = get_db().view('pactcarehq/chw_assigned_patients').all()
    else:
        assignments = get_db().view('pactcarehq/chw_assigned_patients', key=request.user.username).all()

    chw_patient_assignments = {}
    for res in assignments:
        chw = res['key']
        pact_id = res['value'].encode('ascii')
        if not chw_patient_assignments.has_key(chw):
            chw_patient_assignments[chw] = []
        chw_patient_assignments[chw].append(pact_id)

    chw_patient_dict = {}
    for chw in chw_patient_assignments.keys():
        chw_patient_dict[chw] = PactPatient.view('pactcarehq/patient_pact_ids ', keys=chw_patient_assignments[chw], include_docs=True).all()

    #sorted_pts = sorted(patients, key=lambda p: p.couchdoc.last_name)
    #keys = [p.couchdoc.pact_id for p in sorted_pts]
    #context= RequestContext(request)
    #context['chw_patients'] = chw_patient_dict

    chws = sorted(chw_patient_dict.keys())
    #patients = sorted(patients, key=lambda x: x.couchdoc.last_name)
    context['chw_patients_arr'] = [(x, chw_patient_dict[x]) for x in chws]
    return render_to_response(template_name, context_instance=context)


@login_required
def my_patient_activity(request, template_name="pactcarehq/patients_dashboard.html"):
    """Return a list of all the patients in the system"""
    #using per patient instance lookup...slow, but reuasable
    context= RequestContext(request)

    if request.user.is_superuser == True:
        #patients = Patient.objects.all()
        assignments = get_db().view('pactcarehq/chw_assigned_patients').all()
    else:
        assignments = get_db().view('pactcarehq/chw_assigned_patients', key=request.user.username).all()

    chw_patient_dict = {}
    for res in assignments:
        chw = res['key']
        pact_id = res['value'].encode('ascii')
        if not chw_patient_dict.has_key(chw):
            chw_patient_dict[chw] = []
        chw_patient_dict[chw].append(PactPatient.view('pactcarehq/patient_pact_ids', key=pact_id, include_docs=True).first())

    #sorted_pts = sorted(patients, key=lambda p: p.couchdoc.last_name)
    #keys = [p.couchdoc.pact_id for p in sorted_pts]
    #context= RequestContext(request)

    chws = sorted(chw_patient_dict.keys())
    #patients = sorted(patients, key=lambda x: x.couchdoc.last_name)
    context['chw_patients_arr'] = [(x, chw_patient_dict[x]) for x in chws]
    #context['chw_patients'] = chw_patient_dict
    return render_to_response(template_name, context_instance=context)


@login_required
def my_patient_activity_reduce(request, template_name = "pactcarehq/patients_dashboard_reduce.html"):
    #using customized reduce view for the patient dashboard
    context= RequestContext(request)
    dashboards = CActivityDashboard.view('pactcarehq/patient_dashboard', group=True).all()

    context['reduces'] = []
    for reductions in dashboards:
        pact_id = reductions['key']
        dashboard = reductions['value']
        if not dashboard.has_key('patient_doc'):
            continue
        context['reduces'].append(dashboard)
    return render_to_response(template_name, context_instance=context)

def ms_from_timedelta(td):
    """
    Given a timedelta object, returns a float representing milliseconds
    """
    return (td.seconds * 1000) + (td.microseconds / 1000.0)

def do_submission(instance, attachments={}):
    start_time = datetime.utcnow()
    doc = post_xform_to_couch(instance, attachments=attachments)
    delta_post =  datetime.utcnow() - start_time
    logging.debug("Submission posted: %d ms, doc_id: %s" % (ms_from_timedelta(delta_post), doc._id))


@httpdigest()
def get_formhistory(request):
    """Provide a download to send all submitted XForms down to the phone for a given user."""
    restore_id = request.GET.get('since')

@httpdigest()
def debug_casexml_new(request):
    """
    Use the standard way for dimagi.case casexml generation method to get casexml.  This is case OTA Restore for Pact.
    """
    regblock = get_ghetto_registration_block(request.user)
    patient_blocks = [pt.ghetto_xml() for pt in PactPatient.view('patient/search', include_docs=True).all()]
    resp_text = "<restoredata>%s %s</restoredata>" % (regblock, '\n'.join(patient_blocks))
    template_name="pactcarehq/debug_casexml.html"
    context = RequestContext(request)
    context['casexml'] = resp_text
    return render_to_response(template_name, context_instance=context)

@httpdigest()
def get_caselist(request):
    """Intermediary/ghetto way of producing casexml, to be deprecated.
    """
    regblock= get_ghetto_registration_block(request.user)
    patient_block = ""
    patients = PactPatient.view("patient/search", include_docs=True)
    for pt in patients:
        patient_block += pt.ghetto_xml()
    resp_text = "<restoredata>%s %s</restoredata>" % (regblock, patient_block)
    #logging.error(resp_text)

    response = HttpResponse(mimetype='text/xml')
    response.write(resp_text)
    response['Content-Length'] = len(resp_text)
    return response


#@login_required
#def show_ghetto_patientlist(request, template_name="pactcarehq/ghetto_patient_list.html":
#    patients = PactPatient.view("patient/by_last_name")
#    context = RequestContext(request)

@login_required
@cache_page(60 * 5)
def patient_schedule_report(request, patient_id, template_name="pactcarehq/patient_calendar_submit_report.html"):
    """returns a view of the patient's scheduled visits for a given date (which chw it should have been), as well as the visit if there was one
    returns an acheduled_item, ...], [submissions], ...]
    """
    context = RequestContext(request)
    pt = Patient.objects.get(id=patient_id)

    total_interval = 7
    if request.GET.has_key('interval'):
        try:
            total_interval = request.GET['interval']
            if total_interval == "all":
                total_interval = 1000
            else:
                total_interval = int(total_interval)
        except:
            pass


    ret = []
    context['patient'] = pt

    visit_dates = []
    scheduled_by_date = {}
    for n in range(0, total_interval):
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


patient_pactid_cache = {}
def getpatient(pact_id):
    if patient_pactid_cache.has_key(pact_id):
        return patient_pactid_cache[pact_id]
    else:
        pt = PactPatient.view('pactcarehq/patient_pact_ids', key=str(pact_id), include_docs=True).first()
        patient_pactid_cache[pact_id] = pt
        return pt

def _get_schedule_tally(username, total_interval, override_date=None):
    """
    For a given username and interval, get a simple array of the username and scheduled visit (whether a submission is there or not)  exists.
    returns (schedule_tally_array, patient_array, total_scheduled (int), total_visited(int))
    schedul_tally_array = [visit_date, [(patient1, visit1), (patient2, visit2), (patient3, None), (patient4, visit4), ...]]
    where visit = XFormInstance
    """
    if override_date == None:
        nowdate = datetime.now()
        chw_schedule = schedule.get_schedule(username)
    else:
        nowdate = override_date
        chw_schedule = schedule.get_schedule(username, override_date = nowdate)
    #got the chw schedule
    #now let's walk through the date range, and get the scheduled CHWs per this date.visit_dates = []
    ret = [] #where it's going to be an array of tuples:
    #(date, scheduled[], submissions[] - that line up with the scheduled)

    total_scheduled=0
    total_visited=0

    for n in range(0, total_interval):
        td = timedelta(days=n)
        visit_date = nowdate-td
        scheduled_pactids = chw_schedule.get_scheduled(visit_date)
        patients = []
        visited = []
        for pact_id in scheduled_pactids:
            if pact_id == None:
                continue
            try:
                total_scheduled += 1
                cpatient = getpatient(pact_id) #TODO: this is a total waste of queries, doubly getting the cpatient, then getting the django object again
#                patients.append(Patient.objects.get(id=cpatient.django_uuid))
                patients.append(cpatient)
            except:
                continue

        #inefficient, but we need to get the patients in alpha order
        patients = sorted(patients, key=lambda x: x.last_name)
        for patient in patients:
            pact_id = patient.pact_id
            searchkey = [str(username), str(pact_id), visit_date.year, visit_date.month, visit_date.day]
            submissions = XFormInstance.view('pactcarehq/submits_by_chw_per_patient_date', key=searchkey, include_docs=True).all()
            if len(submissions) > 0:
                visited.append(submissions[0])
                total_visited+= 1
            else:
                #ok, so no submission from this chw, let's see if there's ANY from anyone on this day.
                other_submissions = XFormInstance.view('pactcarehq/all_submits_by_patient_date', key=[str(pact_id), visit_date.year, visit_date.month, visit_date.day, 'http://dev.commcarehq.org/pact/dots_form' ], include_docs=True).all()
                if len(other_submissions) > 0:
                    visited.append(other_submissions[0])
                    total_visited+= 1
                else:
                    visited.append(None)

        ret.append((visit_date, zip(patients, visited)))
    return ret, patients, total_scheduled, total_visited



@login_required
def chw_calendar_submit_report_all(request):
    download_id = uuid.uuid4().hex
    total_interval = 7
    if request.GET.has_key('interval'):
        try:
            total_interval = request.GET['interval']
            if total_interval == "all":
                total_interval = 1000
            else:
                total_interval = int(total_interval)
        except:
            pass
    all_chw_submit_report.delay(total_interval, download_id)
    return HttpResponseRedirect(reverse('pactcarehq.views.file_download', kwargs={'download_id': download_id}))

@login_required
def chw_calendar_submit_report(request, username, template_name="pactcarehq/chw_calendar_submit_report.html"):
    """Calendar view of submissions by CHW, overlaid with their scheduled visits, and whether they made them or not."""
    context = RequestContext(request)
    all_patients = request.GET.get("all_patients", False)
    context['username'] = username
    user = User.objects.get(username=username)
    total_interval = 7
    if request.GET.has_key('interval'):
        try:
            total_interval = int(request.GET['interval'])
        except:
            pass

    ret, patients, total_scheduled, total_visited= _get_schedule_tally(username, total_interval)
    nowdate = datetime.now()

    context['date_arr'] = ret
    context['total_scheduled'] = total_scheduled
    context['total_visited'] = total_visited
    #context['total_visited'] = total_visited
    context['start_date'] = ret[0][0]
    context['end_date'] = ret[-1][0]

    if request.GET.get('getcsv', None) != None:
        csvdata = []
        csvdata.append(','.join(['visit_date','assigned_chw','pact_id','is_scheduled','contact_type', 'visit_type','visit_kept', 'submitted_by','visit_id']))
        for date, pt_visit in ret:
            if len(pt_visit) > 0:
                for cpt, v in pt_visit:
                    rowdata = [date.strftime('%Y-%m-%d'), username, cpt.pact_id]
                    if v != None:

                        #is scheduled
                        if v.form['scheduled'] == 'yes':
                            rowdata.append('scheduled')
                        else:
                            rowdata.append('unscheduled')
                        #contact_type
                        rowdata.append(v.form['contact_type'])

                        #visit type
                        rowdata.append(v.form['visit_type'])

                        #visit kept
                        rowdata.append(v.form['visit_kept'])

                        rowdata.append(v.form['Meta']['username'])
                        if v.form['Meta']['username'] == username:
                            rowdata.append('assigned')
                        else:
                            rowdata.append('covered')
                        rowdata.append(v.get_id)
                    else:
                        rowdata.append('novisit')
                    csvdata.append(','.join(rowdata))
            else:
                csvdata.append(','.join([date.strftime('%Y-%m-%d'),'nopatients']))

        resp = HttpResponse()

        resp['Content-Disposition'] = 'attachment; filename=chw_schedule_%s-%s_to_%s.csv' % (username, datetime.now().strftime("%Y-%m-%d"),  (nowdate - timedelta(days=total_interval)).strftime("%Y-%m-%d"))
        resp.write('\n'.join(csvdata))
        return resp

    else:
        return render_to_response(template_name, context_instance=context)

@login_required
def chw_list(request, template_name="pactcarehq/chw_list.html"):
    """A list of all users"""
    context = RequestContext(request)
    q_users = list(User.objects.all().filter(is_active=True).values_list('username', flat=True))

    users = []
    for u in q_users:
        if u.count("_") > 0:
            continue
        users.append(u.encode('ascii'))
    users.sort()

    chw_dashboards = CActivityDashboard.view('pactcarehq/chw_dashboard', keys=users, group=True).all()

    username_dashboard_dict = {}
    for reduction in chw_dashboards:
        chw_username = reduction['key']
        dashboard = CActivityDashboard.wrap(reduction['value'])
        username_dashboard_dict[chw_username] = dashboard
    context['chw_dashboards'] = []
    for uname in users:
        if username_dashboard_dict.has_key(uname):
            context['chw_dashboards'].append((uname, username_dashboard_dict[uname]))
        else:
            context['chw_dashboards'].append((uname, None))
    return render_to_response(template_name, context_instance=context)


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

def _hack_get_old_caseid(new_case_id):
    #hack to test the old ids
    try:
        oldpt = trial1mapping.objects.get(old_uuid=new_case_id)
        old_case_id = oldpt.get_new_patient_doc_id()
    except:
        old_case_id=None
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
    submit_reduction = XFormInstance.view('pactcarehq/all_submits_by_patient_date', keys=keys)
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


def uptime(request):
    response = HttpResponse("success")
    return response


form_xmlns_to_names = {
    'http://dev.commcarehq.org/pact/dots_form': "DOTS",
    'http://dev.commcarehq.org/pact/progress_note': "Progress Note",
    'http://dev.commcarehq.org/pact/bloodwork': "Bloodwork",
    'http://dev.commcarehq.org/pact/mileage': "Mileage",
    'http://dev.commcarehq.org/pact/patientupdate': "Patient Update",
}

def _get_submissions_for_patient(patient):
    """Returns a view of all the patients submissions by the patient's case_id (which is their PactPatient doc_id, this probably should be altered)
    params: patient=Patient (django) object
    returns: array of XFormInstances for a given patient.
    """
    #xform_submissions = XFormInstance.view('pactcarehq/all_submits_by_case', key=patient.doc_id, include_docs=True)
    xform_submissions = XFormInstance.view('pactcarehq/all_submits_by_patient_date', startkey=[patient.couchdoc.pact_id, 0000], endkey=[patient.couchdoc.pact_id, 9999], include_docs=True)
    submissions = []
    for note in xform_submissions:
        xmlns = note['xmlns']
        displayname = form_xmlns_to_names.get(xmlns, None)
        if displayname == None:
            logging.debug("Skipping these namespaces until they are handled correctly %s" % (xmlns))
            continue
        
        if xmlns == 'http://dev.commcarehq.org/pact/dots_form':
            date = note['form']['encounter_date']
        elif xmlns == "http://dev.commcarehq.org/pact/progress_note":
            date = note['form']['note']['encounter_date']
        else:
            try:
                date = note['form']['Meta']['TimeStart'].date()
            except:
                date = datetime.min.date()
        submissions.append([note._id, date, note.form['Meta']['username'] , displayname])
    submissions=sorted(submissions, key=lambda x: x[1], reverse=True)
    return submissions


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
            secs = int(splits[2])
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
        ended = xform.get_form['Meta']['TimeEnd']
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



@httpdigest()
def xml_download(request):
    username = request.user.username

    if username == "ctsims":
        username = 'cs783'
    offset =0
    limit_count=100
    temp_xml = tempfile.TemporaryFile()
    temp_xml.write("<restoredata>\n")
    total_count = 0
    db = get_db()
    xforms = XFormInstance.view("pactcarehq/all_submits", key=username).all()
    for form in xforms:
        try:
            xml_str = db.fetch_attachment(form['id'], 'form.xml').replace("<?xml version=\'1.0\' ?>", '')
            temp_xml.write(xml_str)
            temp_xml.write("\n")
            total_count += 1
        except ResourceNotFound:
            logging.error("Error, xform submission %s does not have a form.xml attachment." % (form._id))
    temp_xml.write("</restoredata>")
    length = temp_xml.tell()
    temp_xml.seek(0)
    wrapper = FileWrapper(temp_xml)
    response = HttpResponse(wrapper, mimetype='text/xml')
    response['Content-Length'] = length
    return response


