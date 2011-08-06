from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from casexml.apps.case.models import CommCareCase
from couchforms.models import XFormInstance
from pactcarehq.forms.weekly_schedule_form import ScheduleForm
from patient import careteam_api
from .util import form_xmlns_to_names
from pactpatient.forms.address_form import SimpleAddressForm
from pactpatient.forms.patient_form import PactPatientForm
from pactpatient.forms.phone_form import PhoneForm
from pactpatient.models.pactmodels import PactPatient, CActivityDashboard
import logging
from patient.views import PatientSingleView

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


        context = super(PactPatientSingleView, self).get_context_data(**kwargs)
        pdoc = context['patient_doc']
        dj_patient = context['patient_django']
        context['patient_list_url'] = reverse('pactpatient_list')
        context['schedule_show'] = schedule_show
        context['schedule_edit'] = schedule_edit
        context['phone_edit'] = phone_edit
        context['address_edit'] = address_edit
        context['patient_edit'] = patient_edit
        context['submit_arr'] = _get_submissions_for_patient(dj_patient)
        context['casedoc'] = CommCareCase.get(pdoc.case_id)

        last_bw = pdoc.last_bloodwork
        context['last_bloodwork'] = last_bw

        role_actor_dict = careteam_api.get_careteam(pdoc.django_patient)
        context['careteam_dict'] = role_actor_dict





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
        if show_all_schedule != None:
            context['past_schedules'] = pdoc.past_schedules




        return context
        #return render_to_response(template_name, context_instance=context)




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
            try:
                date = note['form']['Meta']['TimeStart'].date()
            except:
                date = datetime.min.date()
        submissions.append([note._id, date, note.form['Meta']['username'] , displayname])
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
