from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from carehq_core import carehq_api
from issuetracker.issue_constants import ISSUE_STATE_CLOSED
from issuetracker.models.issuecore import Issue
from patient.forms.address_form import SimpleAddressForm
from patient.forms.phone_form import PhoneForm
from patient.models import Patient
from patient.views import PatientSingleView
from permissions.models import Actor, PrincipalRoleRelation
from datetime import datetime, timedelta

class CarehqPatientSingleView(PatientSingleView):
    #template carehqapp/carehq_patient_base.html
    def get_context_data(self, **kwargs):
        """
        Main patient view for pact.  This is a "do lots in one view" thing that probably shouldn't be replicated in future iterations.
        """
        request = self.request

        schedule_show = request.GET.get("schedule", "active")
        schedule_edit = request.GET.get("edit_schedule", False)
        address_edit = request.GET.get("edit_address", False)
        address_edit_id = request.GET.get("address_id", None)
        new_address = True if request.GET.get("new_address", False) == "True" else False
        phone_edit = request.GET.get("edit_phone", False)
        patient_edit = request.GET.get('edit_patient', None)
        show_all_schedule = request.GET.get('allschedules', None)

        is_me=False
        patient_guid = self.kwargs.get('patient_guid', None)

        if patient_guid is None:
            #verify that this is the patient itself.
            if request.current_actor.is_patient:
                patient_guid = request.current_actor.actordoc.patient_doc_id
                kwargs['patient_guid'] = patient_guid
                is_me=True
            else:
                raise Http404

        #global info
        view_mode = self.kwargs.get('view_mode', '')
        if view_mode == '':
            view_mode = 'info'
        context = super(CarehqPatientSingleView, self).get_context_data(**kwargs)
        context['view_mode'] = view_mode
        context['is_me'] = is_me
        pdoc = context['patient_doc']
        dj_patient = context['patient_django']

        if view_mode == 'issues':
            context['filter'] = request.GET.get('filter', 'recent')
            issues = Issue.objects.filter(patient=dj_patient)
            if context['filter']== 'closed':
                issues = issues.filter(status=ISSUE_STATE_CLOSED)
            elif context['filter'] == 'recent':
                issues = issues.order_by('-last_edit_date')
            elif context['filter'] == 'open':
                issues = issues.exclude(status=ISSUE_STATE_CLOSED)

            context['issues'] = issues
            self.template_name = "carehqapp/patient/carehq_patient_issues.html"
        if view_mode == 'info':
            self.template_name = "carehqapp/patient/carehq_patient_info.html"

        if view_mode == 'careteam':
            context['patient_careteam'] = carehq_api.get_careteam(pdoc)
            self.template_name = "carehqapp/patient/carehq_patient_careteam.html"

        if view_mode == 'careplan':
            self.template_name = "carehqapp/patient/carehq_patient_careplan.html"

        context['patient_list_url'] = reverse('my_patients')
        context['schedule_show'] = schedule_show
        context['schedule_edit'] = schedule_edit
        context['phone_edit'] = phone_edit
        context['address_edit'] = address_edit
        context['patient_edit'] = patient_edit

        context['issue_columns'] = ['opened_date', 'opened_by', 'assigned_to','description', 'last_edit_date', 'last_edit_by']



        if address_edit and not new_address:
            if len(pdoc.address) > 0:
                #if there's an existing address out there, then use it, else, make a new one
                context['address_form'] = SimpleAddressForm(instance=pdoc.get_address(address_edit_id))
            else:
                context['address_form'] = SimpleAddressForm()
        if new_address:
            context['address_form'] = SimpleAddressForm()
            context['address_edit'] = True
        if phone_edit:
            context['phone_form'] = PhoneForm()
        if patient_edit:
            context['patient_form'] = SimplePatientForm(patient_edit, instance=pdoc)
        if show_all_schedule != None:
            context['past_schedules'] = pdoc.past_schedules
        return context
        #return render_to_response(template_name, context_instance=context)

