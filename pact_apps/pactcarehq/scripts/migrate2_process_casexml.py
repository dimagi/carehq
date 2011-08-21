from casexml.apps.case import signals
from couchforms.models import XFormInstance


def run():
    """
    This script will process all submits by in order by date for a given patient.
    """

    print "this migration has been run in production sunday aug 21 2011 at 1:16 am est"
    return
    offset =0
    total = 0
    while True:
        xforms = XFormInstance.view('pactcarehq/all_submits_by_patient_date', include_docs=True, skip=offset, descending=False, limit=100).all()
        if len(xforms) == 0:
            break
        total += 1
        offset += 100

        for form in xforms:
            print "Doc: %s %s (%s)" % (form.doc_type, form.xmlns, form._id)
            signals.process_cases(None, form)
        print "Processed %d" % (total)


