
from shinelabels import label_utils




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


def printer_uptime_email():
    """
    Alerts sent if any adverse printer events would happen
    """

    #if printer went offline and is STILL offline (heartbeat checks)

    #ANY incidents that are NOT successful print or uptime.

    pass



def cleanup_printlogs():
    #once a week?
    label_utils.condense_status_logs()
