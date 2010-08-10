from datetime import datetime
import logging

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponse,Http404, HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q

import uuid

#from django_digest.decorators import *

from ashandapp.forms.provider_register import  NewProviderForm
from provider.models import Provider

less_static_response = """
<restoredata>
           <registration>
                <username>%s</username>
                <password>%s</password>
                <uuid>%s</uuid>
                <date>%s</date>
                <registering_phone_id>%s</registering_phone_id>
                <user_data>
                    <data key="chw_id">%s</data>
                </user_data>
           </registration>
           <case>
                   <case_id>04CBE782D762341234B2E224577A</case_id>
                   <date_modified>2010-05-07T15:52:18.356</date_modified>
                   <create>
                       <case_type_id>cc_path_client</case_type_id>
                       <user_id>3F2504E04F8911D39A0C0305E82C3301</user_id>
                       <case_name>621145448</case_name>
                       <external_id>2</external_id>
                   </create>
                   <update>
                       <pact_id>2</pact_id>
                   </update>
           </case>
           <case>
                   <case_id>04C2412341F3CB825E4B2E224577A</case_id>
                   <date_modified>2010-06-07T15:52:18.356</date_modified>
                   <create>
                       <case_type_id>cc_path_client</case_type_id>
                       <user_id>3F2504E04F8911D39A0C0305E82C3301</user_id>
                       <case_name>631145448</case_name>
                       <external_id>3</external_id>
                   </create>
                   <update>
                       <pact_id>3</pact_id>
                   </update>
           </case>
           <case>
                   <case_id>04CBE782D763453245324224577A</case_id>
                   <date_modified>2010-07-07T15:52:18.356</date_modified>
                   <create>
                       <case_type_id>cc_path_client</case_type_id>
                       <user_id>3F2504E04F8911D39A0C0305E82C3301</user_id>
                       <case_name>551145448</case_name>
                       <external_id>5</external_id>
                   </create>
                   <update>
                       <pact_id>5</pact_id>
                   </update>
           </case>
           <case>
                   <case_id>2341324D32D634F3CB825E4B2E224577A</case_id>
                   <date_modified>2010-04-07T15:52:18.356</date_modified>
                   <create>
                       <case_type_id>cc_path_client</case_type_id>
                       <user_id>3F2504E04F8911D39A0C0305E82C3301</user_id>
                       <case_name>661145448</case_name>
                       <external_id>6</external_id>
                   </create>
                   <update>
                       <pact_id>6</pact_id>
                   </update>
           </case>
        </restoredata>
"""


static_response = """
<restoredata>
           <registration>
                <username>ctsims</username>
                <password>234</password>
                <uuid>3F2504E04F8911D39A0C0305E82C3301</uuid>
                <date>2009-08-12</date>
                <registering_phone_id>3F2504E04F8911D39A0C0305E82C3301</registering_phone_id>
                <user_data>
                    <data key="promoter_id">33</data>
                    <data key="promoter_name">Clayton</data>
                </user_data>
           </registration>
           <case>
                   <case_id>04CBE782D762341234B2E224577A</case_id>
                   <date_modified>2010-05-07T15:52:18.356</date_modified>
                   <create>
                       <case_type_id>cc_path_client</case_type_id>
                       <user_id>3F2504E04F8911D39A0C0305E82C3301</user_id>
                       <case_name>621145448</case_name>
                       <external_id>2</external_id>
                   </create>
                   <update>
                       <pact_id>2</pact_id>
                   </update>
           </case>
           <case>
                   <case_id>04C2412341F3CB825E4B2E224577A</case_id>
                   <date_modified>2010-06-07T15:52:18.356</date_modified>
                   <create>
                       <case_type_id>cc_path_client</case_type_id>
                       <user_id>3F2504E04F8911D39A0C0305E82C3301</user_id>
                       <case_name>631145448</case_name>
                       <external_id>3</external_id>
                   </create>
                   <update>
                       <pact_id>3</pact_id>
                   </update>
           </case>
           <case>
                   <case_id>04CBE782D763453245324224577A</case_id>
                   <date_modified>2010-07-07T15:52:18.356</date_modified>
                   <create>
                       <case_type_id>cc_path_client</case_type_id>
                       <user_id>3F2504E04F8911D39A0C0305E82C3301</user_id>
                       <case_name>551145448</case_name>
                       <external_id>5</external_id>
                   </create>
                   <update>
                       <pact_id>5</pact_id>
                   </update>
           </case>
           <case>
                   <case_id>2341324D32D634F3CB825E4B2E224577A</case_id>
                   <date_modified>2010-04-07T15:52:18.356</date_modified>
                   <create>
                       <case_type_id>cc_path_client</case_type_id>
                       <user_id>3F2504E04F8911D39A0C0305E82C3301</user_id>
                       <case_name>661145448</case_name>
                       <external_id>6</external_id>
                   </create>
                   <update>
                       <pact_id>6</pact_id>
                   </update>
           </case>
        </restoredata>
"""

#@httpdigest
def case_list(request):
    uname = request.user.username
    pwd = request.user.password
    prov_uuid = Provider.objects.get(user=request.user).id
    reg_date = request.user.date_joined
    reg_phone = uuid.uuid1().hex
    chw_guid = uuid.uuid1().hex
    
    resp_txt = less_static_response % (uname, pwd, prov_uuid, reg_date, reg_phone, chw_guid)
    response = HttpResponse(mimetype='text/xml')
    response.write(resp_txt)
    return response
    
@login_required    
def new_provider(request, template_name="ashandapp/edit_provider.html"):    
    context = {}    
    context['form'] = NewProviderForm()
    if request.method == 'POST':
        form = NewProviderForm(data=request.POST)
        if form.is_valid():
            prov = form.save(commit=False)    
            puser = form.get_user()    
            prov.user = puser
            prov.save()                        
            
            return HttpResponseRedirect(reverse('list_cases'))
        else:
            context['form'] = form
            
    return render_to_response(template_name, context, context_instance=RequestContext(request))
    
    
    
