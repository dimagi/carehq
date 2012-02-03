from functools import partial
from django.db.models.signals import post_save, pre_save, post_init
from django.db.models import Q
from issuetracker.issue_constants import ISSUE_STATE_OPEN, ISSUE_STATE_CLOSED
from issuetracker.models import Issue, IssueEvent
import logging
from issuetracker import issue_constants
from patient.models import Patient

def cache_values(sender, instance):
    instance.cache_values = instance.values

def _get_open_issues(patient):
    return patient.issues.all().filter(status=ISSUE_STATE_OPEN)

def _get_closed_issues(patient):
    return patient.issues.all().filter(status=ISSUE_STATE_CLOSED)

def _get_last_activity(patient):
    qset = IssueEvent.objects.select_related('issue','patient').filter(issue__patient=patient).order_by('-created_date')
    if qset.count() > 0:
        return qset[0]
    else:
        return None


def patient_issues_props(sender, instance, **kwargs):
    setattr(instance, 'open_issues', partial(_get_open_issues, instance))
    setattr(instance, 'last_activity', partial(_get_last_activity, instance))
post_init.connect(patient_issues_props, Patient)

def issue_saved(sender, instance, created, **kwargs):
    """
    When a case is saved due to creation
    reversion will automatically save the original information.
    
    However, we will be doing an additional operation to create a IssueEvent to record the actual happening.
    
    Other case events such as making phone calls or doing other work around a case will also be saved,
    but this particular signal will create a IssueEvent of a specific type.
    """
    event_new = IssueEvent()
    event_new.issue = instance
    
    if created:        
        event_create_date = instance.opened_date
        event_creator = instance.opened_by
        notes = "New issue created"
        
        try:
            event_new.activity = issue_constants.ISSUE_EVENT_OPEN
        except Exception, ex:
            logging.error("Error, Event category [%s] activity [%s] does not exist in the database - perhaps the configuration is not fully loaded:: %s" % (instance.category, issue_constants.ISSUE_EVENT_OPEN, ex))
            

    else:
        event_create_date = instance.last_edit_date
        event_creator = instance.last_edit_by
        
        if hasattr(instance, '_save_comment'):
            notes = instance._save_comment
        else:
            notes = "Issue edited"
            
        if hasattr(instance, 'event_activity'):
            event_new.activity = instance.event_activity            
        else:    
            try:
                event_new.activity = ActivityClass.objects.get(event_class=issue_constants.ISSUE_EVENT_EDIT)
            except Exception, ex:
                logging.error("Error, Event Activity does not exist in the database - perhaps the configuration is not fully loaded:: %s" % (ex))
    
    event_new.created_by = event_creator
    event_new.created_date = event_create_date
    event_new.notes = notes    
    event_new.save()    
    
post_save.connect(issue_saved, sender=Issue)