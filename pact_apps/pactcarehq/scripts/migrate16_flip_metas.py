from couchforms.models import XFormInstance
from receiver.signal_emits import scrub_meta


def run():
    #convert patient from pact_id 493 to 199 due to a clerical/data entry accounting error. This should not be done
    #in other circumstances.

    namespaces = [
        #"http://code.javarosa.org/devicereport",
        "http://dev.commcarehq.org/CCPTZ/ccptz_encounter",
        "http://dev.commcarehq.org/pact/bloodwork",
        "http://dev.commcarehq.org/pact/dots_form",
        "http://dev.commcarehq.org/pact/mileage",
        "http://dev.commcarehq.org/pact/patientupdate",
        "http://dev.commcarehq.org/pact/progress_note",
        "http://openrosa.org/app/general",
        "https://www.commcarehq.org/test/casexml-wrapper",
        ]

    for xmlns in namespaces:
        xform_ids = XFormInstance.view('couchforms/by_xmlns', key=xmlns).all()
        for id in xform_ids:
            xform = XFormInstance.get(id)
            scrub_meta(None, xform, None)







