from django.http import HttpResponse
#from pactcarehq.models import trial1mapping
#
#
#
#def _hack_get_old_caseid(new_case_id):
#    #hack to test the old ids
#    try:
#        oldpt = trial1mapping.objects.get(old_uuid=new_case_id)
#        old_case_id = oldpt.get_new_patient_doc_id()
#    except:
#        old_case_id=None
#    return old_case_id
#
#
#


def uptime(request):
    response = HttpResponse("success")
    return response



from api import *
from chw_views import *
from export_views import *
from ota import *
from patient_views import *
from schedule_views import *
from submission_views import *
from .providers import *



