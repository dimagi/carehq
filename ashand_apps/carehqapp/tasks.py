from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from carehq_core import carehq_api
from issuetracker.models.issuecore import Issue

def issue_update_notifications(issue_django_id):
    """
    For a given updated issue, notify people interested in the issue via email that the issue has been updated.
    """
    try:
        issue = Issue.objects.get(id=issue_django_id)
    except Issue.DoesNotExist:
        return
    
    patient_doc = issue.patient.patient_doc
    careteam = carehq_api.get_careteam(patient_doc)
    for prr in careteam:
        actordoc = prr.actor.actordoc
        email = actordoc.email
        if email != '' or email is not None:

            subject = '[ASHand] Issue update notification' #some date/indicator?
            lines = ["Hello %s %s" % (actordoc.first_name, actordoc.last_name)]

            issue_url = "https://ashand.dimagi.com%s" % reverse('manage-issue', kwargs= {'issue_id': issue_id}) #reverse adds the leading /
            lines.append("An issue for someone you are caring for has just been updated.  To view it, please click this link %s" % issue_url)

            body = '\n'.join(lines)
            send_mail(subject, body, 'notifications@dimagi.com', [email], fail_silently=True)
