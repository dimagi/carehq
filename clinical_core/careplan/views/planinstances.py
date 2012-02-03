from django.template import RequestContext
from django.shortcuts import render_to_response
from careplan.models import CarePlanInstance, CarePlanItem


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


