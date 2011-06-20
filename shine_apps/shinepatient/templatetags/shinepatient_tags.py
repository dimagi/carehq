from django import template
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from casexml.apps.case.models import CommCareCase

register = template.Library()

@register.simple_tag
def render_cases(patient):
    cases = CommCareCase.view("shinepatient/cases_by_patient_id", include_docs=True).all()
    return render_to_string("shinepatient/partials/itemlist.html", {"cases": cases})

