import logging
import pdb
import uuid
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from couchforms.util import post_xform_to_couch
from couchforms.views import post as couchforms_post
from receiver.util import spoof_submission


@require_POST
@csrf_exempt
def _do_post(request, callback=None, magic_property='xml_submission_file'):
    """
    Copied from couchforms submission.  need to alter it due to request.POST vs request.FILES
    """
    # odk/javarosa preprocessing. These come in in different ways.
    attachments = {}
    if request.META['CONTENT_TYPE'].startswith('multipart/form-data'):
        #it's an standard form submission (eg ODK)
        #this does an assumption that ODK submissions submit using the form parameter xml_submission_file
        #todo: this should be made more flexibly to handle differeing params for xform submission
        instance = request.FILES[magic_property].read()
        for key, item in request.FILES.items():
            if key != magic_property:
                attachments[magic_property] = item
    elif request.META['CONTENT_TYPE'] == 'application/x-www-form-urlencoded':
        print "getting instance via POST"
        instance = request.POST[magic_property]
        print instance
        for key, item in request.POST.items():
            if key != magic_property:
                attachments[magic_property] = item
    else:
        #else, this is a raw post via a j2me client of xml (or touchforms)
        #todo, multipart raw submissions need further parsing capacity.
        instance = request.raw_post_data

    try:
        doc = post_xform_to_couch(instance, attachments=attachments)
        if callback:
            return callback(doc)
        return HttpResponse("Thanks! Your new xform id is: %s" % doc["_id"], status=201)
    except Exception, e:
        logging.exception(e)
        return HttpResponseServerError("FAIL")

@require_POST
@csrf_exempt
def receive_ccd(request):
    """
    Receive a CCD from the CI push services as per section 14.4 example.
    Returns a 200 response xml fragment.
    """
    #Commented out until couchforms receiver is updated
    #'CONTENT_TYPE': 'multipart/form-data; WORKS - get from request.FILES
    #'CONTENT_TYPE': 'application/x-www-form-urlencoded' FAILS if the request.POST is not populated
    def post_callback(doc):
        response_text = """<Response><Code>SUCCESS</Code><Message>Thank you, doc submitted id:%s</Message></Response>""" % doc['_id']
        return HttpResponse(response_text, content_type='text/xml')
    return _do_post(request, post_callback, magic_property='patientsessiondata')
#    response_text = """<Response><Code>SUCCESS</Code><Message>doc submitted id:%s</Message></Response>""" % doc['_id']

    #Temporary method for submission until receiver logic is updated to handle patientsessiondata POST key
#    payload = None
#    if request.POST.has_key('patientsessiondata'):
#        payload = request.POST['patientsessiondata']
#    else:
#        if request.FILES.has_key('patientsessiondata'):
#            payload = request.FILES['patientsessiondata'].read()
#    if payload is None:
#        logging.error("Error receiving data, patientsession data key not in FILES or POST %s" % str(request.META))
#    resp = spoof_submission(reverse('receiver.views.post'), payload, hqsubmission=False)
#    response_text = "<?xml version=\"1.0\" encoding=\"utf-8\"?><Response><Code>SUCCESS</Code><Message>Thank you %s</Message></Response>" % uuid.uuid4().hex
#    return HttpResponse(response_text, content_type='text/xml') #default this assumes is a 200 response code.

