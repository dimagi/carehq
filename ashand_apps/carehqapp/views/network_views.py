from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from carehq_core import carehq_api
from clinical_shared.decorators import actor_required
from patient.models import Patient
from permissions.models import PrincipalRoleRelation
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import login_required

@login_required
@actor_required
def my_network(request, template="carehqapp/network/my_network.html"):
    context = RequestContext(request)
    #get actor info
    if request.current_actor.is_patient:
        #get careteam info
        pt_careteam = carehq_api.get_careteam(request.current_actor.actordoc.get_couch_patient())
        context['patient_relations'] = pt_careteam
    else:
        all_prrs = carehq_api.get_permissions(request.current_actor.actordoc, direct=True)
        #direct relations
        context['patient_relations'] = all_prrs

        #indirect relations (shared patients)
        patient_ids = all_prrs.values_list('content_id', flat=True)
        connections = PrincipalRoleRelation.objects.filter(content_id__in=patient_ids).exclude(actor=request.current_actor)
        context['connections'] = connections
    return render_to_response(template, context_instance=context)


@login_required
@actor_required
def my_patients(request, template="carehqapp/network/my_patients.html"):
    context = RequestContext(request)

    #get actor info
    #allowed_patients = PrincipalRoleRelation.objects.filter(actor=request.current_actor, content_type=ContentType.objects.get_for_model(Patient)).select_related()
    allowed_patients = carehq_api.get_patients_for_actor(request.current_actor.actordoc)
    context['patient_relations'] = allowed_patients
    return render_to_response(template, context_instance=context)


@login_required
@actor_required
def my_careteam(request, template="carehqapp/network/my_careteam.html"):
    context = RequestContext(request)
    if request.current_actor.is_patient:
        pt_careteam = carehq_api.get_careteam(request.current_actor.actordoc.get_couch_patient())
        context['patient_careteam'] = pt_careteam
    return render_to_response(template, context_instance=context)
