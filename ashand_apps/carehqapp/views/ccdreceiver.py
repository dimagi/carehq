from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from couchforms.views import post as couchforms_post
from receiver.util import spoof_submission

@require_POST
@csrf_exempt
def receive_ccd(request):
    #totally ghetto, but it works
    resp = spoof_submission(reverse('receiver.views.post'), request.POST['patientsessiondata'], hqsubmission=False)
    #def post_callback(doc):
        #response_text = """<Response><Code>SUCCESS</Code><Message>doc submitted id:%s</Message></Response>""" % doc['_id']
        #return HttpResponse(response_text)
    #return couchforms_post(request, post_callback)
    response_text = """<Response><Code>SUCCESS</Code></Response>"""
    #response_text = """<Response><Code>SUCCESS</Code><Message>doc submitted id:%s</Message></Response>""" % doc['_id']
    return HttpResponse(response_text)

