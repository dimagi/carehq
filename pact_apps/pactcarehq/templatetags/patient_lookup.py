from django import template
from pactpatient.models import PactPatient
from patient.models import Patient
from django.core.urlresolvers import reverse

register = template.Library()

@register.simple_tag
def name_from_pactid(xforminstance):
    pt = PactPatient.view('pactcarehq/patient_pact_ids', key=xforminstance.form['pact_id'], include_docs=True).all()
    if len(pt) == 0:
        return "[Unknown Patient]"
    else:
        return "%s %s" % (pt[0].first_name, pt[0].last_name)

@register.simple_tag
def patient_url_from_form(xforminstance):
    pt = PactPatient.view('pactcarehq/patient_pact_ids', key=xforminstance.form['pact_id'], include_docs=True).all()
    if len(pt) == 0:
        return "#"

    djpatient = Patient.objects.filter(doc_id=pt[0]._id)
    if djpatient.count() == 0:
        return "#"
    else:
        return reverse('view_pactpatient', kwargs={'patient_guid':djpatient[0].doc_id, 'view_mode': ''} )