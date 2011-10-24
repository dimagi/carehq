import logging
from celery.decorators import periodic_task
from celery.schedules import crontab
from couchforms.models import XFormInstance
from shinelabels import label_utils
from shinelabels.models import ZebraStatus, ZebraPrinter


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
