from datetime import datetime, timedelta, date
import pdb
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.safestring import mark_safe
import isodate
from auditcare import inspect
from carehq_core import carehq_api
from careplan.models import CarePlanInstance
from casexml.apps.case.models import CommCareCase
from couchforms.models import XFormInstance
from pactcarehq.forms.weekly_schedule_form import ScheduleForm
from pactcarehq.views.dot_calendar import DOTCalendar
from patient.forms.address_form import SimpleAddressForm
from patient.forms.phone_form import PhoneForm
from .util import form_xmlns_to_names
from pactpatient.forms.patient_form import PactPatientForm
from pactpatient.models import PactPatient, CActivityDashboard
import logging
from patient.views import PatientSingleView
from webxforms.views import get_owned_cases

patient_pactid_cache = {}
def getpatient(pact_id):
    if patient_pactid_cache.has_key(pact_id):
        return patient_pactid_cache[pact_id]
    else:
        pt = PactPatient.view('pactcarehq/patient_pact_ids', key=str(pact_id), include_docs=True).first()
        patient_pactid_cache[pact_id] = pt
        return pt

class PactPatientSingleView(PatientSingleView):
    def get_context_data(self, **kwargs):
        """
        Main patient view for pact.  This is a "do lots in one view" thing that probably shouldn't be replicated in future iterations.
        """

        request = self.request
        patient_guid = self.kwargs['patient_guid']

        schedule_show = request.GET.get("schedule", "active")
        schedule_edit = request.GET.get("edit_schedule", False)
        address_edit = request.GET.get("edit_address", False)
        address_edit_id = request.GET.get("address_id", None)
        new_address = True if request.GET.get("new_address", False) == "True" else False
        phone_edit = request.GET.get("edit_phone", False)
        patient_edit = request.GET.get('edit_patient', None)
        show_all_schedule = request.GET.get('allschedules', None)

        view_mode = self.kwargs.get('view_mode', '')
        if view_mode == '':
            view_mode = 'info'
        context = super(PactPatientSingleView, self).get_context_data(**kwargs)


        context['view_mode'] = view_mode

        pdoc = context['patient_doc']
        dj_patient = context['patient_django']


        if view_mode == 'issues':
#            context['filter'] = request.GET.get('filter', 'recent')
#            issues = Issue.objects.filter(patient=dj_patient)
#            if context['filter']== 'closed':
#                issues = issues.filter(status=ISSUE_STATE_CLOSED)
#            elif context['filter'] == 'recent':
#                issues = issues.order_by('-last_edit_date')
#            elif context['filter'] == 'open':
#                issues = issues.exclude(status=ISSUE_STATE_CLOSED)
#
#            context['issues'] = issues
            self.template_name = "pactcarehq/pactpatient/pactpatient_issues.html"
        if view_mode == 'info':
            self.template_name = "pactcarehq/pactpatient/pactpatient_info.html"

        elif view_mode == 'careteam':
            context['patient_careteam'] = carehq_api.get_careteam(pdoc)
            self.template_name = "pactcarehq/pactpatient/pactpatient_careteam.html"

        elif view_mode == 'schedule':
            context['past_schedules'] = pdoc.past_schedules
            self.template_name = "pactcarehq/pactpatient/pactpatient_schedule.html"
        elif view_mode == 'careplan':
            selected_plan_id =  request.GET.get('plan', None)
            if selected_plan_id is not None:
                context['selected_plan'] =  CarePlanInstance.get(selected_plan_id)
                #todo: check for patientguid
            context['careplans'] = CarePlanInstance.view('careplan/by_patient', key=patient_guid, include_docs=True).all()

            self.template_name = "pactcarehq/pactpatient/pactpatient_careplan.html"

        elif view_mode == 'submissions':
            context['submit_arr'] = _get_submissions_for_patient(dj_patient)
            self.template_name = "pactcarehq/pactpatient/pactpatient_submissions.html"
        elif view_mode == 'log':
            history_logs = inspect.history_for_doc(pdoc, filter_fields=['arm','art_regimen','non_art_regimen', 'primary_hp', 'mass_health_expiration', 'hiv_care_clinic'])
            context['history_logs'] = history_logs #[(x, x.get_changed_fields(filters=PactPatient._properties.keys(), excludes=['date_modified'])) for x in audit_logs]

            all_changes = inspect.history_for_doc(pdoc, filter_fields=PactPatient._properties.keys(), exclude_fields=['date_modified'])
            context['all_changes'] = all_changes #[(x, x.get_changed_fields(filters=PactPatient._properties.keys(), excludes=['date_modified'])) for x in audit_logs]
            self.template_name = "pactcarehq/pactpatient/pactpatient_log.html"
        elif view_mode=='dots':
            viewmonth = int(request.GET.get('month', date.today().month))
            viewyear = int(request.GET.get('year', date.today().year))
            cal = DOTCalendar(pdoc).formatmonth(viewyear, viewmonth)
            context['calendar'] = mark_safe(cal)
            self.template_name = 'pactcarehq/pactpatient/pactpatient_dots.html'

        else:
            raise Http404


        context['patient_list_url'] = reverse('pactpatient_list')
        context['schedule_show'] = schedule_show
        context['schedule_edit'] = schedule_edit
        context['phone_edit'] = phone_edit
        context['address_edit'] = address_edit
        context['patient_edit'] = patient_edit
        context['casedoc'] = CommCareCase.get(pdoc.case_id)

        last_bw = pdoc.check_last_bloodwork
        context['last_bloodwork'] = last_bw

        #role_actor_dict = careteam_api.get_careteam(pdoc)


        if last_bw == None:
            context['bloodwork_missing']  = True
        else:
            context['since_bw'] = (datetime.utcnow() - last_bw.get_date).days

            if (datetime.utcnow() - last_bw.get_date).days > 90:
                context['bloodwork_overdue'] = True
            else:
                context['bloodwork_overdue'] = False


        if address_edit and not new_address:
            if len(pdoc.address) > 0:
                #if there's an existing address out there, then use it, else, make a new one
                context['address_form'] = SimpleAddressForm(instance=pdoc.get_address(address_edit_id))
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
            context['patient_form'] = PactPatientForm(patient_edit, instance=pdoc)




#        audit_log_docs = ModelActionAudit.view('auditcare/model_actions', key = ['model_types', 'PactPatient', pdoc._id], include_docs=True).all()
#        audit_log_docs = sorted(audit_log_docs, key=lambda x: x.revision_id, reverse=True)
#        audit_log_info = []
#        for x, l in enumerate(audit_log_docs):
#            if x == len(audit_log_docs)-1:
#                delta = None
#            else:
#                y = x+1
#                removed, added, changed = dict_diff(audit_log_docs[x].archived_data, audit_log_docs[y].archived_data)
#
#            audit_log_info.append((audit_log_docs[x], delta))



        return context




@login_required
def my_patient_activity_grouped(request, template_name="pactcarehq/patients_dashboard.html"):
    """Return a list of all the patients in the system"""
    #using per patient instance lookup...slow, but reuasable
    context= RequestContext(request)

    if request.user.is_superuser == True:
        #patients = Patient.objects.all()
        assignments = PactPatient.get_db().view('pactcarehq/chw_assigned_patients').all()
    else:
        assignments = PactPatient.get_db().view('pactcarehq/chw_assigned_patients', key=request.user.username).all()

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
            if isinstance(note['form']['meta']['timeStart'], datetime):
                date = note['form']['meta']['timeStart'].date()
            else:
                try:
                    timesplit = note['form']['meta']['timeStart'].split(' ')
                    tstring = "%sT%s" % (timesplit[0], timesplit[1])
                    date = isodate.parse_datetime(tstring).date()
                except Exception, e:
                    date = datetime.min.date()
        if not note.form.has_key('meta'):
            username = 'unknown - missing meta!'
            logging.error("Error, submission %s is missing a meta block!" % note._id)
        else:
            username = note.form['meta']['username']
        submissions.append([note._id, date, username , displayname])
    submissions=sorted(submissions, key=lambda x: x[1], reverse=True)
    return submissions



@login_required
def my_patient_activity(request, template_name="pactcarehq/patients_dashboard.html"):
    """Return a list of all the patients in the system"""
    #using per patient instance lookup...slow, but reuasable
    context= RequestContext(request)

    if request.user.is_superuser == True:
        #patients = Patient.objects.all()
        assignments = PactPatient.get_db().view('pactcarehq/chw_assigned_patients').all()
    else:
        assignments = PactPatient.get_db().view('pactcarehq/chw_assigned_patients', key=request.user.username).all()

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
    context['end'] = datetime.utcnow()
    context['start'] = datetime.utcnow() - timedelta(days=14)
    #context['chw_patients'] = chw_patient_dict
    return render_to_response(template_name, context_instance=context)


