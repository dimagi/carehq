from django import template
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from casexml.apps.case.models import CommCareCase
from shinepatient.models import ShinePatient

register = template.Library()

MISSING_DEPENDECY = \
"""Aw shucks, someone forgot to install the google chart library 
on this machine and this feature needs it. To get it, run 
easy_install pygooglechart.  Until you do that this won't work.
"""


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
    
    
#@register.simple_tag
#def case_patient_lookup(case):
#    """
#    For a given case_id, get the patient object back from memcached for fast lookup
#    """
#    #patient emits case id, so we want to match the patient from the case.
#    pts = ShinePatient.view('shinepatient/patient_cases_all', key=case['case_id'], include_docs=True).all()
#    return pts[0]


class PatientFromCaseNode(template.Node):
    def __init__(self, case_obj_passed, var_name):
        self.case = template.Variable(case_obj_passed)
        self.var_name = var_name

    def render(self, context):
        pts = ShinePatient.view('shinepatient/patient_cases_all', key=self.case.resolve(context)['case_id'], include_docs=True).all()
        if len(pts) == 0:
            #raise template.TemplateSyntaxError("Error, tag's argument could not resolve to a CommCareCase")
            context[self.var_name] = None
            return ''
        context[self.var_name] = pts[0]
        return ''


import re
from django import template
def do_get_patient_from_case(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, case_obj_passed, _as, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly two arguments" % token.contents.split()[0])

    return PatientFromCaseNode(case_obj_passed, var_name)





register.tag('case_patient_lookup', do_get_patient_from_case)
