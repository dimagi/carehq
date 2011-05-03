# To manage patient views for create/view/update you need to implement them directly in your patient app
from datetime import datetime
import logging
import urllib
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from patient.models import Patient
from datetime import datetime
from django.core.urlresolvers import reverse

@login_required
def remove_phone(request):
    if request.method == "POST":
        print "got the post for remove_phone"
        try:
            print "trying"
            patient_id = urllib.unquote(request.POST['patient_id']).encode('ascii', 'ignore')
            print "got patient_id"
            patient = Patient.objects.get(id=patient_id)
            print "got patient: %s" % (patient)
            phone_id = urllib.unquote(request.POST['phone_id']).encode('ascii', 'ignore')
            for i, p in enumerate(patient.couchdoc.phones):
                print "iterating through phones: %d: %s" % (i, p)
                if p.phone_id == phone_id:
                    p.deprecated=True
                    p.ended=datetime.utcnow()
                    p.edited_by = request.user.username
                    patient.couchdoc.phones[i] = p
                    patient.couchdoc.save()
            return HttpResponseRedirect(reverse('pactcarehq.views.patient_view', kwargs={'patient_id':patient_id}))
        except Exception, e:
            logging.error("Error getting args:" + str(e))
            #return HttpResponse("Error: %s" % (e))
    else:
        pass



@login_required
def remove_address(request):
    if request.method == "POST":
        print request.POST
        try:
            patient_id = urllib.unquote(request.POST['patient_id']).encode('ascii', 'ignore')
            patient = Patient.objects.get(id=patient_id)
            address_id = urllib.unquote(request.POST['address_id']).encode('ascii', 'ignore')
            patient.couchdoc.remove_address(address_id)
            return HttpResponseRedirect(reverse('pactcarehq.views.patient_view', kwargs={'patient_id':patient_id}))
        except Exception, e:
            logging.error("Error getting args:" + str(e))
            #return HttpResponse("Error: %s" % (e))
    else:
        pass
