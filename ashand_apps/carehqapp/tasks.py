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
