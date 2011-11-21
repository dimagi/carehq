from casexml.apps.case import signals
from couchforms.models import XFormInstance


def run():
    """
    This script will process all submits by in order by date for a given patient.
    """
    xforms = XFormInstance.view('couchforms/by_xmlns', key = 'http://shine.commcarehq.org/questionnaire/labdata', reduce=False, include_docs=True).all()
    for doc in xforms:
        #form.form['case']['case_id'] = 'XN2AH2VPDJ7M9R9P5R6FJS6OK'
        if doc.form['case']['update']['visit_three'] == "yes":
            doc.form['case']['update']['visit_three'] = {"@safe": "yes", "#text": "yes"}
            doc.save()
            print "Doc: %s %s (%s)" % (doc.doc_type, doc.xmlns, doc._id)
        else:
            pass
        #signals.process_cases(None, form)


