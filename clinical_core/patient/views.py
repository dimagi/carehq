# Create your views here.
from django.contrib.auth.decorators import  login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from patient.forms import PactPatientForm
from patient.models.djangomodels import Patient
import urllib
from patient.models.couchmodels import CPhone
from datetime import datetime, datetime
import logging

@login_required
def new_patient(request, template_name="patient/new_patient.html"):
    context = RequestContext(request)
    if request.method == 'POST':
        print "it's a post"
        form = PactPatientForm(data=request.POST)
        #make patient
        if form.is_valid():
            newpatient = Patient()
            newpatient.cset_pact_id(form.cleaned_data['pact_id'])
            newpatient.cset_arm(form.cleaned_data['arm'])
            newpatient.cset_gender(form.cleaned_data['gender'])
            newpatient.cset_birthdate(form.cleaned_data['birthdate'])
            newpatient.cset_art_regimen(form.cleaned_data['art_regimen'])
            newpatient.cset_non_art_regimen(form.cleaned_data['non_art_regimen'])
            newpatient.cset_primary_hp(form.cleaned_data['primary_hp'])
            newpatient.cset_first_name(form.cleaned_data['first_name'])
            newpatient.cset_last_name(form.cleaned_data['last_name'])
            print "going to save"
            newpatient.save()
            print "saved"
            return HttpResponseRedirect(reverse('pactcarehq.views.patient_view', kwargs={'patient_id':newpatient.id}))
        else:
            print "error"
            context['patient_form'] = form
    else:
        print "no error?"
        context['patient_form'] = PactPatientForm()
    return render_to_response(template_name, context_instance=context)


@login_required
def remove_phone(request):
    if request.method == "POST":
        print "got the post for remove_phone"
        try:
            patient_id = urllib.unquote(request.POST['patient_id']).encode('ascii', 'ignore')
            patient = Patient.objects.get(id=patient_id)
            phone_id = urllib.unquote(request.POST['phone_id']).encode('ascii', 'ignore')
            print unicode(phone_id)

            for i in range(0, len(patient.couchdoc.phones)):
                p = patient.couchdoc.phones[i]
                if p.phone_id == phone_id:
                    print "matching phone_id"
                    p.deprecated=True
                    p.ended=datetime.utcnow()
                    p.edited_by = request.user.username
                    patient.couchdoc.phones[i] = p
                    patient.couchdoc.save()
                    break
            return HttpResponseRedirect(reverse('pactcarehq.views.patient_view', kwargs={'patient_id':patient_id}))
        except Exception, e:
            logging.error("Error getting args:" + str(e))
            #return HttpResponse("Error: %s" % (e))
    else:
        pass

