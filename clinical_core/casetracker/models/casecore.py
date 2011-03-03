from itertools import chain

from django.db import models

from django.db.models import Q
from clinical_core.actors.models import Actor

from datetime import datetime, timedelta
from casetracker.middleware import threadlocals

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from casetracker import constants
from patient.models import Patient

from casetracker.managers import CaseManager
from dimagi.utils import make_uuid
import uuid
from django.contrib.contenttypes.models import ContentType
from model_utils.models import InheritanceCastModel



class CaseEvent(models.Model):
    """
    A CaseEvent is any action done revolving around a case.
    A Interaction in our book is an actual medical document that happens for a particular medical document/domain.

    An encounter in this scope is an action that happens and is resolved around a particular case.

    It is meant to capture outside the scope of the case table itself, the actions and their accompanying
    examples of what happened to a case.
    """
    id = models.CharField(_('CaseEvent Unique id'), max_length=32, unique=True, default=make_uuid, primary_key=True) #primary_key override?
    case = models.ForeignKey("Case", related_name='case_events')
    notes = models.TextField(blank=True)

    activity = models.CharField(choices=constants.CASE_EVENT_CHOICES, max_length=160)

    created_date = models.DateTimeField()
    created_by = models.ForeignKey(Actor)
    parent_event = models.ForeignKey("self", blank=True, null=True, related_name="child_events")

    def save(self, unsafe=False):
        if self.id == None:
            self.id = uuid.uuid1().hex
        if unsafe:
            super(CaseEvent, self).save()
            return

        if self.created_date == None:
            if self.created_by == None:
                raise Exception("Missing fields in Case creation - created by")
            self.created_date = datetime.utcnow()
        super(CaseEvent, self).save()

    def __unicode__(self):
        return "Event (%s} by %s on %s" % (self.activity, self.created_by, self.created_date.strftime("%I:%M%p %Z %m/%d/%Y"))

    class Meta:
        app_label = 'casetracker'
        verbose_name = "Case Event"
        verbose_name_plural = "Case Events"
        ordering = ['-created_date']


class Case(models.Model):
    """
    A case in this system is the actual even that needs due diligence and subsequent closure.

    These are finite and discrete tasks that must be done.  Linking these cases to someone or something
    must be implemented elsewhere.

    The scope of these cases are currently attached to the actual agents that need to work on them.

    The uuid should be the primary key, but for the synchronization framework, having a uuid key do all the queries
    and potentially be the primary key should be a top priority.
    """
    id = models.CharField(_('Case Unique id'), max_length=32, unique=True, default=make_uuid, primary_key=True) #primary_key override?

    description = models.CharField(max_length=160)

    category = models.CharField(max_length=160, choices=constants.CATEGORY_CHOICES)
    status = models.CharField(max_length=160, choices=constants.STATUS_CHOICES)
    priority = models.IntegerField(choices=constants.PRIORITY_CHOICES)

    patient = models.ForeignKey(Patient, blank=True, null=True)

    body = models.TextField(blank=True, null=True)


    opened_date = models.DateTimeField()
    opened_by = models.ForeignKey(Actor, related_name="case_opened_by") #cannot be null because this has to have originated from somewhere

    assigned_to = models.ForeignKey(Actor, related_name="case_assigned_to", null=True, blank=True)
    assigned_date = models.DateTimeField(null=True, blank=True)

    last_edit_date = models.DateTimeField(null=True, blank=True)
    last_edit_by = models.ForeignKey(Actor, related_name="case_last_edit_by", null=True, blank=True)

    resolved_date = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(Actor, related_name="case_resolved_by", null=True, blank=True)

    closed_date = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(Actor, related_name="case_closed_by", null=True, blank=True)

    due_date = models.DateTimeField(null=True, blank=True)

    parent_case = models.ForeignKey('self', null=True, blank=True, related_name='child_cases')


    default_objects = models.Manager() # The default manager.
    objects = CaseManager()

    def get_absolute_url(self):
        return "/case/%s" % self.id
        return reverse('manage_case', kwargs={'case_id': self.i})

    @property
    def is_active(self):
        if self.status == constants.CASE_STATE_OPEN:
            return True
        else:
            return False

    @property
    def is_resolved(self):
        if self.status == constants.CASE_STATE_RESOLVED or self.status == constants.CASE_STATE_CLOSED:
            return True
        else:
            return False

    @property
    def is_closed(self):
        if self.status == constants.CASE_STATE_CLOSED:
            return True
        else:
            return False

    @property
    def last_case_event(self):
        #with the models split up for readability, need to make sure no circular dependencies are introduced on import
        if not getattr(self, '_last_case_event', None):
            if CaseEvent.objects.select_related('case', 'activity').filter(case=self).order_by('-created_date').count() > 0:
                self._last_case_event = CaseEvent.objects.filter(case=self).order_by('-created_date')[0]
                return self._last_case_event
            else:
                return None
        else:
            return self._last_case_event


    @property
    def last_event_date(self):
        evt = self.last_case_event
        if evt:
            return evt.created_date
        else:
            return None

    @property
    def last_event_by(self):
        evt = self.last_case_event
        if evt:
            return evt.created_by
        else:
            return None

    def _get_related_objects(self):
        props = dir(self)
        qset_arr = []
        for prop in props:
            #print prop
            if prop == "_base_manager":
                continue
            elif prop == "objects":
                continue
            elif prop == "last_event_date" or prop == "last_event_by" or prop == "last_case_event":
                continue
            elif prop == "related_objects":
                continue
            elif prop == '_get_related_objects':
                continue
            elif prop == 'Meta':
                continue
            elif prop == 'case_events': #skip stuff within myself
                continue

            propclass = getattr(self, prop)

            cls = propclass.__class__.__name__

            if cls == 'RelatedManager' or cls == 'ManyRelatedManager':
                qset_arr.append(propclass.all())
        return list(chain(*qset_arr))

    @property
    def related_objects(self):
        if not hasattr(self, '_related_objects'):
            self._related_objects = self._get_related_objects()
        return self._related_objects

    def save(self, activity=None):
        """
        Save a case.
        Note, this needs to be profoundly updated to be more thread safe using update()
        http://www.slideshare.net/zeeg/db-tips-tricks-django-meetup - look for mccurdy
        """
#        if unsafe:
#            if self.opened_date == None:
#                logging.warning("Case save unsafe: no opened date set")
#            if self.opened_by == None:
#                logging.warning("Case save unsafe: no opened by set")
#            if self.last_edit_date == None:
#                logging.warning("Case save unsafe: no last edit date set")
#            if self.last_edit_by == None:
#                logging.warning("Case save unsafe: no last edit by set")
#            super(Case, self).save()
#            return
#

        if activity == None:
            raise Exception("Error, you must set an ActivityClass for this Case Save")
        else:
            self.event_activity = activity

        if self.last_edit_by == None:
            raise Exception("Missing fields in edited Case: last_edit_by")

        #now, we need to check the status change being done to this.
        if self.status == constants.CASE_STATE_RESOLVED: #from choices of CASE_STATES
            if self.resolved_by == None:
                raise Exception("Case state is now resolved, you must set a resolved_by")
            else:
                self.resolved_date = datetime.utcnow()
        elif self.status == constants.CASE_STATE_CLOSED:
            if self.closed_by == None:
                raise Exception("Case state is now closed, you must set a closed_by")
            else:
                #ok, closed by is set, let's double check that it's been resolved
                if self.resolved_by == None:
                    #raise Exception("Error, this case must be resolved before it can be closed")
                    self.resolved_by = self.closed_by
                    self.resolved_date = datetime.utcnow()
                self.closed_date = datetime.utcnow()

        self.last_edit_date = datetime.utcnow()
        super(Case, self).save()

    def __unicode__(self):
        return "(Case %s) %s" % (self.id, self.description)

    def case_name(self):
        #return "Case %s" % self.id
        return self.description

    def case_name_url(self):
        #return "Case %s" % self.id
        #reverse("casetracker.views.manage_case", args=[obj.id])
        return '<a href="%s">%s</a>' % (reverse('manage-case', args=[self.id]), self.description)

    class Meta:
        app_label = 'casetracker'
        verbose_name = "Case"
        verbose_name_plural = "Cases"
        ordering = ['-opened_date']
