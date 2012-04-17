from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.http import require_POST
from careplan.forms import CarePlanInstanceForm, ChooseBasePlanForm, CarePlanItemForm
from careplan.models import CarePlanInstance, CarePlanItem, BaseCarePlan, CAREPLAN_ITEM_STATES
from clinical_shared.decorators import actor_required
from dimagi.utils.make_time import make_time
from patient.models import BasePatient


def all_careplans(request, template_name = "careplan/all_template_careplans.html"):
    context = dict()
    context['careplans'] = CarePlanInstance.view('careplan/careplan_instances', include_docs=True).all()
    return render_to_response(template_name, context,context_instance=RequestContext(request))

def single_careplan(request, plan_id, template_name = "careplan/view_careplan.html"):
    context = dict()
    context['careplan'] = CarePlanInstance.get(plan_id)
    return render_to_response(template_name, context,context_instance=RequestContext(request))

def single_careplan_item(request, item_id, template_name = "careplan/careplan_items.html"):
    context = dict()
    context['careplan_item'] = CarePlanItem.get(item_id)
    return render_to_response(template_name, context,context_instance=RequestContext(request))


@login_required
@actor_required
def manage_patient_careplan(request, patient_guid, template_name='careplan/manage_patient_careplan.html'):
    context = RequestContext(request)
    patient_doc = BasePatient.get_typed_from_id(patient_guid)

    context['patient_doc'] = patient_doc
    if request.method == "POST":
        print request.POST
        new_item_form = CarePlanInstanceForm(data=request.POST)
        if new_item_form.is_valid():
            plan_instance = new_item_form.save(commit=False)
            plan_instance.patient_guid = patient_guid
            plan_instance.tenant = request.current_actor.actor_tenant.tenant.name

            plan_instance.created_by = "Actor.%s" % request.current_actor.id
            plan_instance.created_date = make_time()

            plan_instance.modified_by = "Actor.%s" % request.current_actor.id
            plan_instance.modified_date = make_time()
            plan_instance.status = CAREPLAN_ITEM_STATES[0][0]
            plan_instance.save()

            context['new_item_form'] = CarePlanInstanceForm() #{'patient_guid': patient_guid, 'tenant': request.current_actor.actor_tenant.tenant.name})
            #drop down to rest of view
        else:
            print "invalid"
            context['new_item_form'] = new_item_form
    else:
        context['new_item_form'] = CarePlanInstanceForm()# {'patient_guid': patient_guid, 'tenant': request.current_actor.actor_tenant.tenant.name})

    context['existing_form'] = ChooseBasePlanForm({'patient_guid': patient_guid, 'tenant': request.current_actor.actor_tenant.tenant.name, })
    context['existing_plans'] = CarePlanInstance.view('careplan/by_patient', key=patient_guid, include_docs=True).all()


    plan_id = request.GET.get('plan_id', None)
    if plan_id is not None:
        careplan_instance = CarePlanInstance.get(plan_id)
        context['careplan_instance'] = careplan_instance
        context['careplan_item_form'] = CarePlanItemForm()

    return render_to_response(template_name, context)


@require_POST
@actor_required
def link_template_careplan_for_patient(request) :
    """
    Link an existing template careplan to a patient by copying it into a CarePlanInstance first
    """
    plan_id = request.POST['base_plan']
    patient_guid = request.POST['patient_guid']
    tenant = request.POST['tenant']
    template=BaseCarePlan.get(plan_id)
    new_instance = CarePlanInstance.create_from_template(template)

    new_instance.status=CAREPLAN_ITEM_STATES[0][0]
    new_instance.patient_guid = patient_guid

    new_instance.created_by = "Actor.%s" % request.current_actor.id
    new_instance.modified_by = "Actor.%s" % request.current_actor.id
    new_instance.tenant = request.current_actor.actor_tenant.tenant.name

    new_instance.save()
    return HttpResponseRedirect(reverse('manage_patient_careplan', kwargs={'patient_guid':patient_guid}))


@require_POST
@actor_required
def new_patient_careplan_item(request, patient_guid, plan_id):
    """
    For a given CarePlanInstance ID, make a new CarePlanItem to place within it.
    """
    careplan_instance = CarePlanInstance.get(plan_id)
    new_item_form = CarePlanItemForm(data=request.POST)
    if new_item_form.is_valid():
        new_item = new_item_form.save(commit=False)

        new_item.created_by = "Actor.%s" % request.current_actor.id
        new_item.modified_by = "Actor.%s" % request.current_actor.id

        new_item.created_date = make_time()
        new_item.modified_date = make_time()

        careplan_instance.plan_items.append(new_item)
        careplan_instance.modified_by = "Actor.%s" % request.current_actor.id
        careplan_instance.modified_date = make_time()
        careplan_instance.save()
        return HttpResponseRedirect(reverse('manage_patient_careplan', kwargs={'patient_guid':patient_guid}) + "?plan_id=%s" % plan_id)