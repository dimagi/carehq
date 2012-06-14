import pdb
from xml.etree import ElementTree
import isodate
from casexml.apps.case.models import CommCareCase
from casexml.apps.case.signals import process_cases
from casexml.apps.case.tests.util import CaseBlock
from couchforms.signals import xform_saved
import logging
import simplejson
from django.core.cache import cache
from couchforms.util import post_xform_to_couch
from dimagi.utils.make_time import make_time
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

                    #reconcile and resubmit DOT json - commcare2.0
                    dots_data = pts[0].get_dots_data()
                    case = CommCareCase.get(pdoc.case_id)
                    if case.opened_on is None:
                        #hack calculate the opened on date from the first xform
                        opened_date = case.actions[0].date
                    else:
                        opened_date = case.opened_on

                    owner_id = case.owner_id
                    update_dict = {'dots': simplejson.dumps(dots_data)}

                    caseblock = CaseBlock(case._id, update=update_dict, owner_id=owner_id, external_id=pdoc.pact_id, case_type='', date_opened=opened_date, close=False, date_modified=make_time().strftime("%Y-%m-%dT%H:%M:%SZ"))
                    #'2011-08-24T07:42:49.473-07') #make_time())

                    def isodate_string(date):
                        if date: return isodate.datetime_isoformat(date) + "Z"
                        return ""

                    case_blocks = [caseblock.as_xml(format_datetime=isodate_string)]

                    form = ElementTree.Element("data")
                    form.attrib['xmlns'] = "http://dev.commcarehq.org/pact/patientupdate"
                    form.attrib['xmlns:jrm'] ="http://openrosa.org/jr/xforms"
                    for block in case_blocks:
                        form.append(block)
                    xform = ElementTree.tostring(form)
                    xform_posted = post_xform_to_couch(ElementTree.tostring(form))
                    process_cases(sender="dotsupdate", xform=xform_posted)

        except Exception, ex:
            logging.error("Error, dots submission did not have a dots block in the update section: %s" % (ex))

    except:
        logging.error("Error processing the submission due to an unknown error.")

xform_saved.connect(process_dots_submission)

