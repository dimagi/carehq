from casexml.apps.case.models import CommCareCase
from couchforms.signals import xform_saved
import logging
import simplejson
from shinepatient.models import ShinePatient
from receiver.signals import successful_form_received

def process_shinepatient_registration(sender, xform, **kwargs):
    try:
        if xform.xmlns != "http://shine.commcarehq.org/patient/reg":
            return
        try:
            case_id = xform['form']['case']['case_id']
            case_doc = CommCareCase.get(case_id)
            patient_guid = case_doc['patient_guid']
            external_id = case_doc['external_id']
            # TODO: communicate anything here?
            newptdoc = ShinePatient()
            newptdoc._id = patient_guid
            newptdoc.external_id = external_id
            newptdoc.first_name = case_doc['first_name']
            newptdoc.last_name = case_doc['last_name']
            #newptdoc.middle_name = case_doc['middle_name']
            newptdoc.gender = case_doc['sex']
            newptdoc.birthdate = case_doc['dob']
            newptdoc.save()

        except Exception, ex:
            logging.error("Error, dots submission did not have a dots block in the update section: %s" % (ex))
            print "error signal 1: %s" % (ex)

    except:
        logging.error("Error processing the submission due to an unknown error.")
        raise

successful_form_received.connect(process_shinepatient_registration)

