from django import template
from patient.models.couchmodels import CPatient
from patient.models.djangomodels import Patient
from django.core.urlresolvers import reverse

register = template.Library()

@register.simple_tag
def name_from_pactid(xforminstance):
    pt = CPatient.view('pactcarehq/patient_pactids', key=xforminstance.form['pact_id'], include_docs=True).all()
    if len(pt) == 0:
        return "[Unknown Patient]"
    else:
        return "%s %s" % (pt[0].first_name, pt[0].last_name)

@register.simple_tag
def patient_url_from_form(xforminstance):
    pt = CPatient.view('pactcarehq/patient_pactids', key=xforminstance.form['pact_id'], include_docs=True).all()
    if len(pt) == 0:
        return "#"

    djpatient = Patient.objects.filter(doc_id=pt[0]._id)
    if djpatient.count() == 0:
        return "#"
    else:
        return reverse('view_patient', kwargs={'patient_id':djpatient[0].id} )