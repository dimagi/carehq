from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from carehq_core import carehq_api
from issuetracker.models.issuecore import Issue
from patient.forms.address_form import SimpleAddressForm
from patient.forms.phone_form import PhoneForm
from patient.models import Patient
from patient.views import PatientSingleView
from permissions.models import Actor, PrincipalRoleRelation
from datetime import datetime, timedelta

def my_patients(request, template="carehqapp/my_patients.html"):
    context = RequestContext(request)

    #get actor info
    allowed_patients = PrincipalRoleRelation.objects.filter(actor=request.current_actor, content_type=ContentType.objects.get_for_model(Patient)).select_related()

    pt_relation_dict = {}

    for prole in allowed_patients:
        for_role = pt_relation_dict.get(prole.role, [])
        for_role.append(prole.content)
        pt_relation_dict[prole.role] = for_role

    context['patient_relations'] = pt_relation_dict
    return render_to_response(template, context_instance=context)


class AshandPatientSingleView(PatientSingleView):
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


        context = super(AshandPatientSingleView, self).get_context_data(**kwargs)
        pdoc = context['patient_doc']
        dj_patient = context['patient_django']
        context['patient_list_url'] = reverse('my_patients')
        context['schedule_show'] = schedule_show
        context['schedule_edit'] = schedule_edit
        context['phone_edit'] = phone_edit
        context['address_edit'] = address_edit
        context['patient_edit'] = patient_edit

        context['issue_columns'] = ['opened_date', 'opened_by', 'assigned_to','description', 'last_edit_date', 'last_edit_by']
        context['issues'] = Issue.objects.filter(patient=dj_patient)


        role_actor_dict = carehq_api.get_careteam_dict(pdoc)
        context['careteam_dict'] = role_actor_dict

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

