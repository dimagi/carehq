from couchforms.signals import xform_saved
import logging
import simplejson
from pactpatient import caseapi
from pactpatient.models import PactPatient

def process_dots_submission(sender, xform, **kwargs):
    try:
        if xform.xmlns != "http://dev.commcarehq.org/pact/dots_form":
            return
        try:
            dots_json = xform['form']['case']['update']['dots']
            if isinstance(dots_json, str) or isinstance(dots_json, unicode):
                json_data = simplejson.loads(dots_json)
                xform['pact_data'] = {}
                xform['pact_data']['dots'] = json_data
                xform.save()

                #next, we recache the casedoc as well as the ota restore fragment of this patient.
                pact_id = xform['form']['pact_id']
                pts= PactPatient.view('pactcarehq/patient_pact_ids', key=pact_id, include_docs=True).all()
                if len(pts) == 1:
                    pts[0]._cache_case(invalidate=True)
                    caseapi.recompute_dots_casedata(pts[0])
        except Exception, ex:
            logging.error("Error, dots submission did not have a dots block in the update section: %s" % (ex))

    except:
        logging.error("Error processing the submission due to an unknown error.")

xform_saved.connect(process_dots_submission)

