from django import template
from django.core.urlresolvers import reverse
from ashandapp.models import CareTeam

register = template.Library() 
 
@register.simple_tag
def patient_for_case(case):    
    return CareTeam.objects.get(cases=case).patient


