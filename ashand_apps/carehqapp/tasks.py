from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from carehq_core import carehq_api
from issuetracker.models.issuecore import Issue
from celery.decorators import task

@task
def issue_update_notifications(issue_django_id):
    """
    For a given updated issue, notify people interested in the issue via email that the issue has been updated.
    """
    try:
        issue = Issue.objects.get(id=issue_django_id)
    except Issue.DoesNotExist:
        return
    
    patient_doc = issue.patient.couchdoc
    careteam = carehq_api.get_careteam(patient_doc)
    for prr in careteam:
        actordoc = prr.actor.actordoc
        email = actordoc.email
        if email != '' or email is not None:

            subject = '[ASHand] Issue update notification' #some date/indicator?
            lines = ["Hello %s," % (actordoc.first_name )]

            issue_url = "https://ashand.dimagi.com%s" % reverse('manage-issue', kwargs= {'issue_id': issue.id}) #reverse adds the leading /
            lines.append("An issue for someone you are caring for has just been updated.  To view it, please click this link:" \
" %s\n" % issue_url)

            lines.append("""
Because this issue contains sensitive personal information, we ask that you please log on to ashand.dimagi.com to view it.

Should you have any questions or comments, please feel free to add them to the issue at ashand.dimagi.com. For security purposes, comments may only be added to your issues via the ashand website. Emailed replies to this notification message will not be received by ASHand staff.

Thank you,
ASHand System

Dimagi Inc.
585 Massachusetts Avenue Suite 3
Cambridge, MA 02139, USA

Confidentiality Notice: This e-mail message (including any attachments or embedded documents) is intended for the
exclusive and confidential use of the individual or entity to which this message is addressed, and unless otherwise
expressly indicated, is confidential and privileged information of Dimagi. Any dissemination, distribution or copying
of the enclosed material is prohibited. If you receive this transmission in error, please notify us immediately by
e-mail at security@dimagi.com and delete the original message.  Your cooperation is appreciated.
            """)

            body = '\n'.join(lines)
            send_mail(subject, body, 'ashand-system@dimagi.com', [email], fail_silently=True)
