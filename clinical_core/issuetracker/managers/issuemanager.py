from django.db import models
from datetime import datetime

class IssueManager(models.Manager):
    def get_authored(self, actor, patient=None, category=None):
        """Return a queryset authored (opened_by) an actor.
        Additional optional filtration by patient and category"""
        qset = super(IssueManager, self).get_query_set().filter(opened_by=actor)
        if patient:
            qset = qset.filter(patient=patient)
        if category:
            qset = qset.filter(category=category)
        return qset

    def get_edited(self, actor, patient=None, category=None):
        """Return a queryset edited (last_edit_by) an actor.
        Additional optional filtration by patient and category"""
        qset = super(IssueManager, self).get_query_set().filter(last_edit_by=actor)
        if patient:
            qset = qset.filter(patient=patient)
        if category:
            qset = qset.filter(category=category)
        return qset

    def get_closed(self, actor, patient=None, category=None):
        """Return a queryset closed (closed_by) an actor.
        Additional optional filtration by patient and category"""
        qset = super(IssueManager, self).get_query_set().filter(closed_by=actor)
        if patient:
            qset = qset.filter(patient=patient)
        if category:
            qset = qset.filter(category=category)
        return qset

    def get_for_patient(self, patient):
        """Return a queryset of cases that are linked to a patient.  Technically this is redundant to the patient instance method for getting cases"""
        qset = super(IssueManager, self).get_query_set().filter(patient=patient)
        return qset

    def get_all_activities(self, actor, patient=None, category=None, activity=None):
        """Returns a queryset of any case touched by actor with other filtrations
        """
        qset = super(IssueManager, self).get_query_set().filter(issue_events__created_by=actor)
        if patient:
            qset = qset.filter(patient=patient)
        if activity:
            qset = qset.filter(activity=activity)
        if category:
            qset = qset.filter(category=category)
        return qset

    def new_issue(self, category, creator_actor, description, body, priority, patient=None, status=None, activity=None, other_data=None, assigned_actor=None, *args, **kwargs):
        """
        Create a new case of an arbitrary type, with the basic requirements for creating a case.
        Other arguments: commit=True - save the created case to the db immediately.

        other_data is an argument for a piece of arbitrary data to link to this case.
        """
        newissue = self.model()
        newissue.category = category
        newissue.priority = priority

        if status != None:
            newissue.status = status
        newissue.description = description
        newissue.body = body

        #auto defined information
        newissue.opened_date = datetime.utcnow()
        newissue.opened_by = creator_actor
        newissue.last_edit_date = newissue.opened_date #this causes some issues with the basic queries, so we will set it to be the same as opened date
        newissue.last_edit_by = newissue.opened_by

        if patient != None:
            newissue.patient=patient

        newissue.save(creator_actor, activity=activity)
        return newissue


        