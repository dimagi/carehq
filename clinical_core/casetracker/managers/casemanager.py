from django.db import models
from datetime import datetime

class CaseManager(models.Manager):
    def new_case(self, category, creator_actor, description, body, priority, status=None, other_data=None, *args, **kwargs):
        """
        Create a new case of an arbitrary type, with the basic requirements for creating a case.
        Other arguments: commit=True - save the created case to the db immediately.
        
        other_data is an argument for a piece of arbitrary data to link to this case.
        """
        newcase = self.model()        
        newcase.category = category        
        newcase.priority = priority
        
        if status != None:
            newcase.status = status
        #newcase.status = Status.objects.filter(category=newcase.category).filter(state_class=constants.CASE_STATE_OPEN)[0] #get the default opener - this is a bit sketchy
        newcase.description = description
        newcase.body = body
        
        
        #auto defined information
        newcase.opened_date = datetime.utcnow()
        newcase.opened_by = creator_actor
        newcase.last_edit_date = newcase.opened_date #this causes some issues with the basic queries, so we will set it to be the same as opened date
        newcase.last_edit_by = newcase.opened_by
        newcase.orig_description = newcase.description        
        
        newcase.save()        
        return newcase
        
    
        