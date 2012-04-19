from couchforms.signals import xform_saved
import logging
from shinepatient.models import ShinePatient
from django.core.cache import cache

def process_patient_submission(sender, xform, **kwargs):
    try:
        try:
            case_id = xform['form']['case']['case_id']
            pts = ShinePatient.view('shinepatient/patient_cases_all', key=case_id, include_docs=True).all()
            if len(pts) == 1:
                #pts[0]._do_get_latest_case(invalidate=True)
                cache.delete('shinepatient_latest_case_%s' % pts[0]._id)
                cache.delete('patient_matrix_%s' % pts[0]._id)
                cache.delete('patient_last_action_%s' % pts[0]._id, None)
                for case_id in pts[0].cases:
                    attrib = '_case_submissions_%s' % case_id
                    cache.delete(attrib)



        except Exception, ex:
            print ex
            logging.error("Error, patient update submission did not have data in correct format: %s" % (ex))

    except Exception, ex:
        print "outer error"
        print ex
        logging.error("Error processing the submission due to an unknown error.")
xform_saved.connect(process_patient_submission)

