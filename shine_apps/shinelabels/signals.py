from datetime import datetime
import math
from django.core.mail import send_mail
from django.db.models.signals import post_save
from casexml.apps.case.models import CommCareCase
import logging
import settings
from shineforms.constants import STR_MEPI_LAB_ONE_FORM
from shinelabels.models import LabelQueue, ZebraPrinter, ZebraStatus
from shinelabels.zpl_templates import case_qr_zpl, lab_datamatrix_zpl
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
        if xform.xmlns != STR_MEPI_LAB_ONE_FORM:
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



def generate_case_barcode(case_id, num=10, mode='qr'):
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
    if mode == 'qr':
        return case_qr_zpl % label_data
    else:
        return lab_datamatrix_zpl % label_data



def status_saved(sender, instance, created, **kwargs):
    """
    post-save signal for checking uptime indicator and emailing where appropriate
    """
    current_printer = instance.printer
    current_status = instance.status
    body = ''
    subject=''
    if instance.status == 'printer uptime heartbeat':
        #do the checking workflow
        if instance.is_cleared:
            is_now_online=True
        else:
            is_now_online=False

        prior_states = ZebraStatus.objects.all().filter(printer=current_printer, status=current_status).order_by('-event_date')
        for prior_state in prior_states:
            if prior_state.id == instance.id:
                #skip if we run into ourselves
                continue
            if prior_state.is_cleared:
                #Previously the printer was ONLINE
                if is_now_online:
                    #and now it is ONLINE
                    #that's good, do nothing, we're done
                    break
                else:
                    #it is OFFLINE after being previously ONLINE
                    send_mail('[MEPI-OPS] Printer %s Offline' % current_printer.name, 'Printer %s is now offline' % current_printer.name, settings.EMAIL_HOST_USER, settings.ALERT_EMAILS, fail_silently=True)
                    break
            else:
                #previously the printer was OFFLINE
                if is_now_online:
                    #but now it's ONLINE.  This is good!  Let's tell people it's online now.
                    send_mail('[MEPI-OPS] Printer %s back online' % current_printer.name, 'Printer %s back online' % current_printer.name, settings.EMAIL_HOST_USER, settings.ALERT_EMAILS, fail_silently=True)
                    break
                else:
                    #previously OFFLINE and still OFFLINE
                    #todo, consider checking deeper and report if it's been offline for a long while.
                    break
    else:
        #send an email for NEW alerts that are bad. Skip print job completed
        if instance.is_cleared == False and instance.status != 'pq job completed':
            #send_email of error
            send_mail('[MEPI-OPS] Printer Alert', "Printer %s: %s" % (current_printer.name, instance.status) , settings.EMAIL_HOST_USER, settings.ALERT_EMAILS, fail_silently=True)
        pass


post_save.connect(status_saved, sender=ZebraStatus)

