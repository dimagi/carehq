from corehq.apps.case import signals
from couchforms.models import XFormInstance


def run():
    offset = 0
    while True:

        xforms = XFormInstance.view('pactcarehq/all_submits', include_docs=True, skip=offset, limit=100).all()
        if len(xforms) == 0:
            break
        offset += 100

        for form in xforms:
            print form.
            signals.process_cases(None, form)
        print "Processed %d" % (offset)


