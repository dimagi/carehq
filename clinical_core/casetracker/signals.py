from django.db.models.signals import post_save, pre_save
from django.db.models import Q
from models import Case, CaseEvent, ActivityClass
import logging
from casetracker import constants

def case_saved(sender, instance, created, **kwargs):
    """
    When a case is saved due to creation
    reversion will automatically save the original information.
    
    However, we will be doing an additional operation to create a CaseEvent to record the actual happening.
    
    Other case events such as making phone calls or doing other work around a case will also be saved,
    but this particular signal will create a CaseEvent of a specific type.
    """
    event_new = CaseEvent()
    event_new.case = instance
    
    if created:        
        event_create_date = instance.opened_date
        event_creator = instance.opened_by
        notes = "New case created by " + event_creator.get_full_name()
        
        try:
            event_new.activity = ActivityClass.objects.filter(category=instance.category).get(event_class=constants.CASE_EVENT_OPEN)
        except Exception, ex:
            logging.error("Error, Event category [%s] activity [%s] does not exist in the database - perhaps the configuration is not fully loaded:: %s" % (instance.category, constants.CASE_EVENT_OPEN, ex))
            

    else:
        event_create_date = instance.last_edit_date
        event_creator = instance.last_edit_by
        
        if hasattr(instance, 'save_comment'):
            notes = instance.save_comment
        else:
            notes = "Case edited by " + event_creator.get_full_name()
            
        if hasattr(instance, 'event_activity'):
            event_new.activity = instance.event_activity            
        else:    
            try:
                event_new.activity = ActivityClass.objects.filter(category=instance.category).get(event_class=constants.CASE_EVENT_EDIT)
            except Exception, ex:
                logging.error("Error, Event Activity does not exist in the database - perhaps the configuration is not fully loaded:: %s" % (ex))
    
    event_new.created_by = event_creator
    event_new.created_date = event_create_date
    event_new.notes = notes    
    event_new.save()    
    
post_save.connect(case_saved, sender=Case)