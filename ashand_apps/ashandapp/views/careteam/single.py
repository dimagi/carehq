from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext


@login_required
#@is_careteam_member
def single(request, careteam_id, template_name="carehqapp/careteam/view_careteam.html"):
    context = RequestContext(request)
#    careteam = CareTeam.objects.get(id=careteam_id)
#
#    context['careteam'] = careteam
#
#    cases = careteam.cases.all()
#    context['cases'] = cases
#    context['patient']= careteam.patient
#
#    context['careteam'] = careteam
#    cases = careteam.cases.all()
#    context['cases'] = cases
#
#    context['careplan'] = TemplateCarePlan.objects.all()[0]
#    context['show_children'] = True
#    context['plan_items'] = context['careplan'].templatecareplanitemlink_set.all()
    raise Exception("careteam.single view not implemented - need to correct and use new actor framework")
    
    return render_to_response(template_name, context_instance=context)


@login_required
#@is_careteam_member
def single_history(request, careteam_id, template_name="carehqapp/careteam/view_careteam_history.html"):
    context = {}
#    careteam = CareTeam.objects.get(id=careteam_id)
#
#    context['careteam'] = careteam
#
#    cases = careteam.cases.all()
#    context['cases'] = cases
#    context['patient']= careteam.patient
#
#    context['careteam'] = careteam
#    cases = careteam.cases.all()
#    context['cases'] = cases
#
#    context['careplan'] = TemplateCarePlan.objects.all()[0]
#    context['show_children'] = True
#    context['plan_items'] = context['careplan'].templatecareplanitemlink_set.all()
#
#
    raise Exception("careteam.single_history view not implemented - need to correct and use new actor framework")
    return render_to_response(template_name, context, context_instance=RequestContext(request))


@login_required
#@is_careteam_member
def single_careplan(request, careteam_id, template_name="carehqapp/careteam/view_careteam_careplan.html"):
    context = {}
#    careteam = CareTeam.objects.get(id=careteam_id)
#
#    context['careteam'] = careteam
#
#    cases = careteam.cases.all()
#    context['cases'] = cases
#    context['patient']= careteam.patient
#
#    context['careteam'] = careteam
#    cases = careteam.cases.all()
#    context['cases'] = cases
#
#    context['careplan'] = TemplateCarePlan.objects.all()[0]
#    context['show_children'] = True
#    context['plan_items'] = context['careplan'].templatecareplanitemlink_set.all()
    raise Exception("careteam.single_careplan not implemented - need to correct and use new actor framework")
    
    
    return render_to_response(template_name, context, context_instance=RequestContext(request))
