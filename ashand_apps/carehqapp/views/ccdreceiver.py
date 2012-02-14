import logging
import pdb
import uuid
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from carehq_core import carehq_api
from carehqapp.models import CCDSubmission
from clinical_shared.decorators import actor_required
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
        instance = request.POST[magic_property]
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



@login_required
@actor_required
def submissions_list(request, internal_id, template_name="carehqapp/ccd_submissions.html"):
    context = RequestContext(request)
    #hack till we get it all stitched up
    sk=[internal_id, 0000]
    ek = [internal_id, 3000]
    context['submissions']=CCDSubmission.view('carehqapp/ccd_submissions_by_patient', startkey=sk, endkey=ek, include_docs=True).all()
    return render_to_response(template_name, context_instance=context)

@login_required
@actor_required
def view_ccd(request, doc_id, template_name='carehqapp/view_ccd.html'):
    context = RequestContext(request)
    submit = CCDSubmission.get(doc_id)
    patient_doc=submit.get_patient_doc()
    context['submit']=submit

    if not carehq_api.has_permission(request.current_actor.actordoc, patient_doc) and not request.user.is_superuser:
        raise PermissionDenied
    return render_to_response(template_name, context_instance=context)

