from casexml.apps.case.models import CommCareCase
from couchforms.signals import xform_saved
import logging
import simplejson
from django.core.cache import cache
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
                case_id = xform['form']['case']['case_id']
                pts= PactPatient.view('pactpatient/by_case_id', key=case_id, include_docs=True).all()
                if len(pts) == 1:
                    pts[0]._cache_case(invalidate=True)
                    pts[0].get_ghetto_regimen_xml(invalidate=True)

        except Exception, ex:
            logging.error("Error, dots submission did not have a dots block in the update section: %s" % (ex))

    except:
        logging.error("Error processing the submission due to an unknown error.")

xform_saved.connect(process_dots_submission)

