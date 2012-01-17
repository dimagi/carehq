from django.contrib.contenttypes.models import ContentType
from django.db import models
from datetime import datetime
from django.db.models.query_utils import Q
from patient.models.patientmodels import Patient
from permissions.models import PrincipalRoleRelation

class IssueManager(models.Manager):

    def care_issues(self, actor):
        """
        Get issues for the patients in their care
        """
        flat_permissions = PrincipalRoleRelation.objects.filter(actor=actor)
        ptype = ContentType.objects.get_for_model(Patient)
        patient_prrs = flat_permissions.filter(content_type=ptype)
        patient_ids = set(patient_prrs.values_list('content_id', flat=True))
        qset = super(IssueManager, self).get_query_set().filter(patient__id__in=patient_ids).select_related('patient','opened_by','created_by','last_edit_by')
        return qset

    def get_relevant(self, actor, patient=None):
        """
        Returns any case relevant of interest.
        """
        q_opened = Q(opened_by=actor)
        q_edited = Q(last_edited_by=actor)
        q_resolved = Q(resolved_by=actor)
        q_closed = Q(closed_by=actor)

        qset = super(IssueManager, self).get_query_set().filter(q_opened | q_edited | q_resolved | q_closed)
        if patient:
            qset = qset.filter(patient=patient)
        return qset

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

    def get_assigneed(self, actor, patient=None, category=None):
        """Return a queryset closed (assigned_to) an actor.
        Additional optional filtration by patient and category"""
        qset = super(IssueManager, self).get_query_set().filter(assigned_to=actor)
        if patient:
            qset = qset.filter(patient=patient)
        if category:
            qset = qset.filter(category=category)
        return qset

    def get_resolved(self, actor, patient=None, category=None):
        """Return a queryset closed (resolved_by) an actor.
        Additional optional filtration by patient and category"""
        qset = super(IssueManager, self).get_query_set().filter(resolved_by=actor)
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

    def new_issue(self, category, creator_actor, description, body, priority, patient=None, status=None, activity=None,
                  other_data=None, assigned_actor=None, *args, **kwargs):
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
            newissue.patient = patient

        newissue.save(creator_actor, activity=activity)
        return newissue


        