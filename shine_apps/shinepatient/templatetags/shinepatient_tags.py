from django import template
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from casexml.apps.case.models import CommCareCase

register = template.Library()

MISSING_DEPENDECY = \
"""Aw shucks, someone forgot to install the google chart library 
on this machine and this feature needs it. To get it, run 
easy_install pygooglechart.  Until you do that this won't work.
"""

@register.simple_tag
def render_cases(patient = None):
    if patient is not None:
        cases = CommCareCase.view("shinepatient/cases_by_patient_id", include_docs=True,
                                  key=patient.get_id).all()
    else:
        cases = CommCareCase.view("shinepatient/cases_by_patient_id", include_docs=True).all()
    
    
    return render_to_string("shinepatient/partials/itemlist.html", {"patient": patient, 
                                                                    "cases": cases})

@register.simple_tag
def render_barcode(barcode):
    try:
        from pygooglechart import QRChart
    except ImportError:
        raise Exception(MISSING_DEPENDECY)
    HEIGHT = WIDTH = 150
    code = QRChart(HEIGHT, WIDTH)
    code.add_data(barcode)
    return '<p style="font-weight: bold;">Scan Item Here: </p><img src="%(url)s" title="%(barcode)s" />' \
            % {"url": code.get_url(), "barcode": barcode} 
    
    
