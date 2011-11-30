__author__ = 'ternus'

from clinical_core.simplecareplan.models import *
from clinical_core.simplecareplan.forms import *
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.template.context import RequestContext
from django.contrib import messages
from django.http import HttpResponseRedirect



def careplan(request, user_id=None, template_name="carehqapp/careplan.html"):
    context = RequestContext(request)

    if not user_id:
        user = request.user
    else:
        user = get_object_or_404(User, pk=user_id)
    careplan = get_object_or_404(CarePlan, patient=user)
    context["patient"] = user
    context["careplan"] = careplan
    context["careplan_elements"] = careplan.elements.all()
    return render_to_response(template_name, context)

def edit_careplan(request, user_id=None, template_name="carehqapp/edit_careplan.html"):
    context = RequestContext(request)

    if user_id is "" or user_id is None:
        user = request.user
    else:
        user = get_object_or_404(User, pk=user_id)
    careplan = get_object_or_404(CarePlan, user=user)
    context["patient"] = user

    if request.method == 'POST':
        form = CarePlanEditForm(data=request.POST)
        if form.is_valid():
            careplan.text = form.cleaned_data['content']
            careplan.save()
            messages.add_message(request, messages.SUCCESS, "Updated care plan.")
            return HttpResponseRedirect("/") #TODO redirect somewhere reasonable
    else:
        context["form"] = CarePlanEditForm({"content": careplan.text})

    return render_to_response(template_name, context)

    