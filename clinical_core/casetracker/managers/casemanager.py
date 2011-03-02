from datetime import datetime
import logging
from casetracker.models.casecore import Case

class CaseManager(object):
    """
    CaseManager is a wrapper function to make a manager-like accessor for the couchdb Case document class
    """

    def get_case(self, case_id):
        if Case.view('casetracker/cases_by_id',key=case_id).count() == 0:
            return None
        else:
            return Case.view('casetracker/cases_by_id',key=case_id, include_docs=True).first()

    def get_authored(self, actor, patient=None, category=None):
        """Return a view result of cases opened_by an actor.
        Additional optional filtration by patient and category"""
        if patient != None:
            logging.warning("Patient filtering is not implemented yet")
        if category != None:
            logging.warning("Category filtering is not implemented yet")
        results = Case.view('casetracker/by_actor', key=['opened_by', actor.id]).all()
        return results

    def get_edited(self, actor, patient=None, category=None):
        """Return a queryset edited (last_edit_by) an actor.
        Additional optional filtration by patient and category"""
        results = Case.view('casetracker/by_actor', key=['last_edit_by', actor.id]).all()
        return results

    def get_closed(self, actor, patient=None, category=None):
        """Return a queryset closed (closed_by) an actor.
        Additional optional filtration by patient and category"""
        results = Case.view('casetracker/by_actor', key=['closed_by', actor.id]).all()
        return results

    def get_for_patient(self, patient):
        """Return a queryset of cases that are linked to a patient.  Technically this is redundant to the patient instance method for getting cases"""
        if patient == None:
            results =Case.view('casetracker/by_patient', key=None).all()
        else:
            results = Case.view('casetracker/by_patient', key=patient.id).all()
        return results

    def actor_activities(self, actor, patient=None, category=None, activity=None):
        """Returns a queryset of any case touched by actor with other filtrations
        """
        qset = super(CaseManager, self).get_query_set().filter(case_events__created_by=actor)
        if patient:
            qset = qset.filter(patient=patient)
        if activity:
            qset = qset.filter(activity=activity)
        if category:
            qset = qset.filter(category=category)
        return qset

    def new_case(self, category, creator_actor, description, body, priority, patient=None, status=None, activity=None, other_data=None, *args, **kwargs):
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
        #newcase.status = Status.objects.filter(state_class=constants.CASE_STATE_OPEN)[0] #get the default opener - this is a bit sketchy
        newcase.description = description
        newcase.body = body

        #auto defined information
        newcase.opened_date = datetime.utcnow()
        newcase.opened_by = creator_actor
        newcase.last_edit_date = newcase.opened_date #this causes some issues with the basic queries, so we will set it to be the same as opened date
        newcase.last_edit_by = newcase.opened_by
        newcase.orig_description = newcase.description
        if patient != None:
            newcase.patient=patient

#        if activity == None:
            #activity=ActivityClass.objects.filter()

        newcase.save(activity=activity)
        return newcase
        
    
        