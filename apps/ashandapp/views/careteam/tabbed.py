from django.shortcuts import render_to_response

from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from ashandapp.models import CaseProfile, CareTeam,ProviderLink
from patient.models import Patient
from casetracker.queries.caseevents import get_latest_event, get_latest_for_cases

from ashandapp.decorators import is_careteam_member

@login_required
@is_careteam_member
def view_careteam(request, careteam_id, template_name="ashandapp/view_careteam_tabbed.html"):    
    context = {}
    careteam = CareTeam.objects.get(id=careteam_id)
    #careteam.
    
    context['careteam'] = careteam                
    cases = careteam.cases.all()
    context['cases'] = cases    
    context['patient']= careteam.patient
    context['careplan'] = """Lorem ipsum dolor sit amet,  Nulla nec tortor. Donec id elit quis purus consectetur consequat. 
                            Nam congue semper tellus. Sed erat dolor, dapibus sit amet, venenatis ornare, ultrices ut, nisi. Aliquam ante. Suspendisse scelerisque dui nec velit. 
                            Duis augue augue, gravida euismod, vulputate ac, facilisis id, sem.  Morbi in orci. Nulla purus lacus, pulvinar vel, malesuada ac, mattis nec, quam. 
                            Nam molestie scelerisque quam. Nullam feugiat cursus lacus.orem ipsum dolor sit amet, consectetur adipiscing elit. 
                            Donec libero risus, commodo vitae, pharetra mollis, posuere eu, pede. Nulla nec tortor. Donec id elit quis purus consectetur consequat. 
                            Nam congue semper tellus. Sed erat dolor, dapibus sit amet, venenatis ornare, ultrices ut, nisi. Aliquam ante. 
                            Suspendisse scelerisque dui nec velit. Duis augue augue, gravida euismod, vulputate ac, facilisis id, sem. Morbi in orci. 
                            Nulla purus lacus, pulvinar vel, malesuada ac, mattis nec, quam. Nam molestie scelerisque quam. Nullam feugiat cursus lacus.orem ipsum dolor sit amet, 
                            consectetur adipiscing elit. Donec libero risus, commodo vitae, pharetra mollis, posuere eu, pede. Nulla nec tortor. Donec id elit quis purus consectetur consequat. 
                            Nam congue semper tellus. Sed erat dolor, dapibus sit amet, venenatis ornare, ultrices ut, nisi. Aliquam ante. </p><p>Suspendisse scelerisque dui nec velit. Duis augue augue, gravida euismod, 
                            vulputate ac, facilisis id, sem. Morbi in orci. Nulla purus lacus, pulvinar vel, malesuada ac, mattis nec, quam. Nam molestie scelerisque quam. Nullam feugiat cursus lacus.orem ipsum dolor sit amet, 
                            consectetur adipiscing elit. Donec libero risus, commodo vitae, pharetra mollis, posuere eu, pede. Nulla nec tortor. Donec id elit quis purus consectetur consequat. 
                            Nam congue semper tellus. Sed erat dolor, dapibus sit amet, venenatis ornare, ultrices ut, nisi."""
    
    provider_links_raw = careteam.providerlink_set.all()
    provider_dict = {}
    
    for plink in provider_links_raw:
        prov = plink.provider        
        provider_dict[prov] = plink
    context['provider_dict'] = provider_dict
    
    return render_to_response(template_name, context, context_instance=RequestContext(request))
