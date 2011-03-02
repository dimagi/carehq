from django.contrib.auth.decorators import  login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.models import User
from forms import AddProviderForm
from models.roles import Doctor

import logging

def addProvider(request, template="addProvider.html"):
    context = RequestContext(request)
    if request.method == 'POST':
        form = AddProviderForm(data=request.POST)
        if form.is_valid():
            u = User()
            u.first_name = form.cleaned_data['first_name']
            u.last_name = form.cleaned_data['last_name']
            u.username = form.cleaned_data['username']
            u.set_password("testpass")
            u.save()
            d = Doctor()
            d.title = form.cleaned_data['title']
            d.department = form.cleaned_data['department']
            d.specialty = form.cleaned_data['specialty']
            d.user = u
            d.save()
            return HttpResponseRedirect("/")
        else:
            print "oh no an error"
            print form
            
    else:
        context['form'] = AddProviderForm()
    return render_to_response(template, context)



def view_actor(request, actor_id, template="actors/single_actor.html"):
    context = RequestContext(request)
    return render_to_response(template, context)
