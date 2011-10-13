from datetime import datetime
import math
from casexml.apps.case.models import CommCareCase
import logging
from shinelabels.models import LabelQueue, ZebraPrinter
from shinelabels.zpl_templates import case_qr_zpl
from receiver.signals import successful_form_received
from django.contrib.auth.models import User
from django.db import models
from tastypie.models import create_api_key


#enabling api key authentication for tastypie for API access
models.signals.post_save.connect(create_api_key, sender=User)

def process_lab_one_submission(sender, xform, **kwargs):
    """
    If ANY bottle comes up positive, fire up the print job for processing
    """
    try:
        if xform.xmlns != "http://shine.commcarehq.org/lab/one":
            return
        try:
            positives = xform['form']['positive_bottles'].split(' ')

            lq = LabelQueue()
            lq.case_guid = xform['form']['case']['case_id']
            lq.destination=ZebraPrinter.objects.all()[0]
            lq.created_date = datetime.utcnow()
            lq.xform_id = xform._id
            lq.zpl_code=generate_case_barcode(lq.case_guid)
            lq.save()
        except Exception, ex:
            logging.error("Error, shine lab data submission: %s" % (ex))
            print "error making label %s" % ex

    except:
        logging.error("Error processing the jsubmission due to an unknown error.")
        raise
successful_form_received.connect(process_lab_one_submission)



def generate_case_barcode(case_id, num=10):
    """
    For a given case ID, we need to construct a barcode for the patient.
    """
    case = CommCareCase.get(case_id)
    #we are assuming that case == patient and bloodwork here.
    label_data = dict()
    label_data['barcode_data']=case_id # case_id?
    label_data['last_name']= case.last_name
    label_data['first_name']= case.first_name
    label_data['gender']= case.sex.title()[0]
    label_data['age']= int(math.floor((datetime.utcnow().date() - case.dob).days / 365.25))
    #label_data['external_id']= case.external_id #add this later if we ever get to making a human readable/transcribable number
    label_data['enroll_date']= case.opened_on.strftime('%d/%m/%Y')
    label_data['print_num'] = num

    return case_qr_zpl % label_data

