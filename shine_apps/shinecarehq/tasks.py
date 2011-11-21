import logging
import tempfile
from celery.schedules import crontab
from celery.task import task, periodic_task
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
import simplejson
from couchexport.export import export
from couchexport.models import Format
from couchforms.models import XFormInstance
from shinelabels import label_utils
from django.core.cache import cache


@task
def schema_export(namespace, download_id, email=None):
    cache_container = {}
    tmp = tempfile.NamedTemporaryFile(suffix='.xls', delete=False)
    if export(namespace, tmp, format=Format.XLS):
        cache_container['mimetype'] = 'application/vnd.ms-excel'
        cache_container['Content-Disposition'] = 'attachment; filename=%s.xls' % namespace
        cache_container['location'] = tmp.name
        tmp.close()
    else:
        cache_container = {}
        cache_container['mimetype'] = 'text/plain'
        cache_container['location'] = None
        cache_container['message'] = "No data due to an error generating the file"
    cache.set(download_id, simplejson.dumps(cache_container), 86400)

    if email != None:
        subject = "[CareHQ] Your requested file download is ready"
        url = "https://pact.dimagi.com" + reverse('retrieve_download', kwargs={'download_id': download_id})
        body = '\n'.join(['To retrieve your document log into CareHQ and visit the URL below.', url])
        send_mail(subject, body, 'notifications@dimagi.com', [email], fail_silently=True)


@periodic_task(run_every=crontab(hour=23, minute=59))
def prime_views():
    """
    Cheater function to hit certain key views in pact so as to keep the view index refreshes low.
    """
    db = XFormInstance.get_db()
    schema_index = "http://dev.commcarehq.org/pact/progress_note"
    db.view("couchexport/schema_index", key=schema_index, include_docs=True, limit=5).all()
    logging.debug("Primed couchexport/schema_index")

    db.view("shinecarehq/all_submits_by_date", limit=5).all()
    logging.debug("Primed shinecarehq/all_submits_by_date")

    db.view("shinepatient/patient_cases_all", limit=5).all()
    logging.debug("Primed shinepatient views")


    #shared code
    db.view("patient/all", limit=5).all()
    logging.debug("Primed patient views")

    db.view("case/by_last_date", limit=5).all()
    logging.debug("Primed case views")

    db.view("auditcare/by_date", limit=5).all()
    logging.debug("Primed auditcare views")

    db.view("actorpermission/all_actors", limit=5).all()
    logging.debug("Primed actorpermission views")

@periodic_task(run_every=crontab(hour=23, minute=59))
def daily_admin_emails():
    """
    Daily study progress emails to study admins.  To be sent before the 1:30pm meeting.
    """

    #new enrollments
    #current status
    #positive results
    #yesterday's activities
    #stale patients (no activity)

    #bloodwork 5 day alert

    pass


#@periodic_task(run_every=crontab(hour=0))
def printer_uptime_email():
    """
    Alerts sent if any adverse printer events would happen
    """


    pass





@periodic_task(run_every=crontab(day_of_week='sunday', hour=23, minute=59))
def cleanup_printlogs():

    """
    Cleanup the printer status messages
    """
    label_utils.condense_status_logs()
