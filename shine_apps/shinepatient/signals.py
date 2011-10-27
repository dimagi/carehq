import uuid
from casexml.apps.case.models import CommCareCase
from couchforms.signals import xform_saved
import logging
import simplejson
from shineforms.constants import STR_MEPI_ENROLLMENT_FORM
from shinepatient.models import ShinePatient
from receiver.signals import successful_form_received
from django.core.files.base import ContentFile
from slidesview.models import ImageAttachment
   
def process_shinepatient_registration(sender, xform, **kwargs):
    try:
        if xform.xmlns != STR_MEPI_ENROLLMENT_FORM:
            return
        try:
            case_id = xform['form']['case']['case_id']
            case_doc = CommCareCase.get(case_id)

            newptdoc = ShinePatient()
            newptdoc.external_id = case_doc['external_id']
            newptdoc.first_name = case_doc['first_name']
            newptdoc.last_name = case_doc['last_name']
            newptdoc.gender = case_doc['sex']
            newptdoc.birthdate = case_doc['dob']
            newptdoc.cases.append(case_id)
            newptdoc.save()

        except Exception, ex:
            logging.error("Error, shine patient submission: %s" % (ex))

    except:
        logging.error("Error processing the submission due to an unknown error.")
        raise
successful_form_received.connect(process_shinepatient_registration)


