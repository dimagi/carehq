from django.db.models.signals import post_save, pre_save
from django.db.models import Q
from models import Case, CaseEvent, EventActivity
import logging

def case_saved(sender, instance, created, **kwargs):
    """
    When a case is saved due to creation and/or modification
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
        notes = "New case created by " + str(event_creator)
        qname = Q(event_class='open')
    else:
        event_create_date = instance.last_edit_date
        event_creator = instance.last_edit_by
        
        if hasattr(instance, 'edit_comment'):
            notes = instance.edit_comment
        else:
            notes = "Case edited by " + str(event_creator)
        qname = Q(event_class='edit')
    try:
        event_new.activity = EventActivity.objects.filter(category=instance.category).get(qname)
    except:
        logging.error("Error, a 'New Case' Event Activity does not exist for this system")
    
    event_new.created_by = event_creator
    event_new.created_date = event_create_date
    event_new.notes = notes    
    event_new.save()    
    
post_save.connect(case_saved, sender=Case)