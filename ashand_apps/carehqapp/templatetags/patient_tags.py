from django import template

register = template.Library() 
 
@register.simple_tag
def patient_for_case(case):    
    #return CareTeam.objects.get(cases=case).patient
    raise Exception("not fixed to reflect new actor models")

