from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response



#see all care plans or template care plans
from django.views.decorators.http import require_POST
from careplan.forms import BaseCarePlanForm, BaseCarePlanItemForm, ChooseBaseCarePlanForm
from careplan.models import BaseCarePlan, BaseCarePlanItem
from dimagi.utils.make_time import make_time

def all_template_careplans(request, template_name = "careplan/all_template_careplans.html"):
    context = {}    
    context['template_careplans'] = BaseCarePlan.view('careplan/template_careplans', startkey=[request.current_actor.actor_tenant.tenant.name], endkey=[request.current_actor.actor_tenant.tenant.name, {}], include_docs=True).all()
    return render_to_response(template_name, context,context_instance=RequestContext(request))


#see individual care plan or template careplan
def single_template_careplan(request, plan_id, template_name="careplan/view_template_careplan.html"):
    context = {}
    context['show_children'] = True    
    context['careplan'] = BaseCarePlan.get(plan_id)

    context['add_form'] = ChooseBaseCarePlanForm()
    context['new_form'] = BaseCarePlanItemForm()
    return render_to_response(template_name, context,context_instance=RequestContext(request))


def all_template_items(request, template_name = "careplan/all_template_items.html"):
    context = {}    
    roots_only = False
    context['plan_items'] = BaseCarePlanItem.view('careplan/template_items', include_docs=True).all()
    return render_to_response(template_name, context,context_instance=RequestContext(request))

def single_template_item(request, item_id, template_name = "careplan/template_item.html"):
    context = {}    
    context['plan_item'] = BaseCarePlanItem.get(item_id)
    return render_to_response(template_name, context,context_instance=RequestContext(request))

def new_template_careplan(request, template_name='careplan/new_template_careplan.html'):
    context={}
    if request.method == "POST":
        form = BaseCarePlanForm(data=request.POST)
        if form.is_valid():
            base_careplan = form.save(commit=False)
            base_careplan.created_by = "Actor.%s" % request.current_actor.id
            base_careplan.created_date = make_time()

            base_careplan.modified_by = "Actor.%s" % request.current_actor.id
            base_careplan.modified_date = make_time()
            base_careplan.save()
            return HttpResponseRedirect(reverse('careplan.views.caretemplates.single_template_careplan', kwargs={'plan_id':base_careplan._id}))
    else:
        context['form'] = BaseCarePlanForm()
    return render_to_response(template_name, context,context_instance=RequestContext(request))


def new_template_item(request, template_name='careplan/new_template_item.html'):
    context={}
    if request.method == "POST":
        form = BaseCarePlanItemForm(data=request.POST)
        if form.is_valid():
            base_item = form.save(commit=False)
            base_item.created_by = "Actor.%s" % request.current_actor.id
            base_item.created_date = make_time()

            base_item.modified_by = "Actor.%s" % request.current_actor.id
            base_item.modified_date = make_time()
            base_item.save()
            return HttpResponseRedirect(reverse('careplan.views.caretemplates.single_template_item', kwargs={'plan_id':base_item._id}))
    else:
        context['form'] = BaseCarePlanItemForm()
    return render_to_response(template_name, context,context_instance=RequestContext(request))

@require_POST
def add_new_item_to_template(request, plan_id):
    template = BaseCarePlan.get(plan_id)
    form = BaseCarePlanItemForm(data=request.POST)
    if form.is_valid():
        base_item = form.save(commit=False)
        base_item.created_by = "Actor.%s" % request.current_actor.id
        base_item.created_date = make_time()

        base_item.modified_by = "Actor.%s" % request.current_actor.id
        base_item.modified_date = make_time()
        base_item.save()
        #add it to the database, then add it to the template

        template.plan_items.append(base_item)
        template.save()
        return HttpResponseRedirect(reverse('careplan.views.caretemplates.single_template_careplan', kwargs={'plan_id':template._id}))

@require_POST
def add_existing_item_to_template(request, plan_id) :
    item_id = request.POST['template_item_id']
    template=BaseCarePlan.get(plan_id)
    item = BaseCarePlanItem.get(item_id)
    template.plan_items.append(item)
    template.save()
    return HttpResponseRedirect(reverse('careplan.views.caretemplates.single_template_careplan', kwargs={'plan_id':template._id}))





