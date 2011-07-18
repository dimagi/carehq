from casexml.apps.case import signals
from couchforms.models import XFormInstance


def run():
    """
    This script will process all submits by in order by date for a given patient.
    """
    xforms = XFormInstance.view('couchforms/by_xmlns', key = 'http://shine.commcarehq.org/bloodwork/entry', reduce=False, include_docs=True).all()
    for form in xforms:
        print form
        form.form['case']['case_id'] = 'XN2AH2VPDJ7M9R9P5R6FJS6OK'
        form.save()
        print "Doc: %s %s (%s)" % (form.doc_type, form.xmlns, form._id)
        signals.process_cases(None, form)


