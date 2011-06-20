from django import template
from django.core.urlresolvers import reverse
from patient.models.patientmodels import BasePatient

register = template.Library()

@register.simple_tag
def patient_url(patient):
    if isinstance(patient, basestring):
        patient = BasePatient.get_typed_from_dict\
                        (BasePatient.get_db().get(patient))
    # hackity hack
    if hasattr(patient, "view_name") and patient.view_name:
        return reverse(patient.view_name, args=[patient.get_id])
    return reverse("single_patient", args=[patient.get_id])
    