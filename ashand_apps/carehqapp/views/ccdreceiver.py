import uuid
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from couchforms.views import post as couchforms_post
from receiver.util import spoof_submission

@require_POST
@csrf_exempt
def receive_ccd(request):
    """
    Receive a CCD from the CI push services as per section 14.4 example.
    Returns a 200 response xml fragment.
    """
    #Commented out until couchforms receiver is updated
    #def post_callback(doc):
    #response_text = """<Response><Code>SUCCESS</Code><Message>doc submitted id:%s</Message></Response>""" % doc['_id']
    #return HttpResponse(response_text)
    #return couchforms_post(request, post_callback)
    #response_text = """<Response><Code>SUCCESS</Code><Message>doc submitted id:%s</Message></Response>""" % doc['_id']

    #Temporary method for submission until receiver logic is updated to handle patientsessiondata POST key
    resp = spoof_submission(reverse('receiver.views.post'), request.POST['patientsessiondata'], hqsubmission=False)
    response_text = "<?xml version=\"1.0\" encoding=\"utf-8\"?><Response><Code>SUCCESS</Code><Message>Thank you %s</Message></Response>" % uuid.uuid4().hex
    return HttpResponse(response_text) #default this assumes is a 200 response code.

