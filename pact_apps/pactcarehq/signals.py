import pdb
from couchforms.signals import xform_saved
import logging
from pactpatient.models import PactPatient

def process_patient_update_submission(sender, xform, **kwargs):
    try:
        if xform.xmlns != "http://dev.commcarehq.org/pact/patientupdate":
            return
        try:

            case_id = xform['form']['case'].get('case_id', None)
            if case_id is None:
                case_id = xform['form']['case'].get('@case_id', None)


            pts = PactPatient.view('pactpatient/by_case_id', key=case_id, include_docs=True).all()

            if len(pts) == 1:
                pts[0].clear_case_cache()
        except Exception, ex:
            logging.error("Error, patient update submission did not have data in correct format: %s" % (ex))
            logging.error("XForm: %s" % xform.to_json())

    except:
        logging.error("Error processing the submission due to an unknown error.")
xform_saved.connect(process_patient_update_submission)

