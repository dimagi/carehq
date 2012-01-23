from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from carehq_core import carehq_api
from patient.models import Patient
from permissions.models import PrincipalRoleRelation

def my_network(request, template="carehqapp/my_network.html"):
    context = RequestContext(request)
    #get actor info
    if request.current_actor.is_patient:
        #get careteam info
        pt_careteam = carehq_api.get_careteam(request.current_actor.actordoc.get_couch_patient())
        context['patient_careteam'] = pt_careteam
    all_prrs = carehq_api.get_permissions(request.current_actor.actordoc)
    context['all_relations'] = all_prrs
    return render_to_response(template, context_instance=context)