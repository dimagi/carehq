from corehq.apps.case import signals
from couchforms.models import XFormInstance


def run():
    """
    This script will process all submits by in order by date for a given patient.
    """
    offset =0
    while True:

        xforms = XFormInstance.view('pactcarehq/all_by_patient_date', include_docs=True, skip=offset, descending=False, limit=100).all()
        if len(xforms) == 0:
            break
        offset += 100

        for form in xforms:
            print "Doc: %s %s (%s)" % (form.doc_type, form.xmlns, form._id)
            signals.process_cases(None, form)
                #print "\tError processing casexml: %s: %s" % (form._id, ex)
        print "Processed %d" % (offset)


