from couchforms.signals import xform_saved
import logging
import simplejson
from pactpatient import caseapi
from pactpatient.models import PactPatient

def process_dots_submission(sender, xform, **kwargs):
    try:
        if xform.xmlns != "http://dev.commcarehq.org/pact/dots_form":
            return

        #first, set the pact_data to json if the dots update stuff is there.
        try:
            dots_json = xform['form']['case']['update']['dots']
            if isinstance(dots_json, str) or isinstance(dots_json, unicode):
                json_data = simplejson.loads(dots_json)
                xform['pact_data'] = {}
                xform['pact_data']['dots'] = json_data
                xform.save()
        except Exception, ex:
            #if this gets triggered, that's ok because web entry don't got them
            logging.debug("Error, dots submission did not have a dots block in the update section: %s" % (ex))

        # next get pact_id information first off
        pact_id = xform['form']['pact_id']
        pts= PactPatient.view('pactcarehq/patient_pact_ids', key=pact_id, include_docs=True).all()
        for pt in pts:
            pt._cache_case(invalidate=True)
            caseapi.recompute_dots_casedata(pt)
    except:
        logging.error("Error processing the submission due to an unknown error.")

xform_saved.connect(process_dots_submission)

