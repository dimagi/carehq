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
from dimagi.utils import make_uuid, make_time
import uuid
from django.contrib.contenttypes.models import ContentType
from model_utils.models import InheritanceCastModel
from couchdbkit.ext.django.schema import Document
from couchdbkit.schema.properties import StringProperty, StringProperty, DateTimeProperty, DateTimeProperty, IntegerProperty, BooleanProperty
from couchdbkit.schema.properties_proxy import SchemaListProperty, SchemaProperty
from dimagi.utils.couch import database

CASE_EVENT_CHOICES = (
        (constants.CASE_EVENT_OPEN, 'Open/Create'), #case state
        (constants.CASE_EVENT_VIEW, 'View'),
        (constants.CASE_EVENT_EDIT, 'Edit'),
        (constants.CASE_EVENT_WORKING, 'Working'), #working on case?  this seems a bit ridiculous
        (constants.CASE_EVENT_REOPEN, 'Reopen'), #case state
        (constants.CASE_EVENT_COMMENT, 'Comment'),
        (constants.CASE_EVENT_CUSTOM, 'Custom'), #custom are activities that don't resolve around the basic open/edit/view/resolve/close
        (constants.CASE_EVENT_RESOLVE, 'Resolve'), #case status state
        (constants.CASE_EVENT_CLOSE, 'Close'), #case status state
    )

#ok, this is a bit nasty, but the rationale is, an actual CASE only really has 3 states. open, resolved and closed
#the case_state_chjocies are acutal events that happen AROUND a case, that can alter the state of a case.


CASE_STATES = (
        (constants.CASE_STATE_OPEN, 'Open'),
        (constants.CASE_STATE_RESOLVED, 'Resolved'),
        (constants.CASE_STATE_CLOSED, 'Closed'),
)


class Priority(Document):
    """
    Priorities are assigned on a case basis, and are universally assigned.
    Sorting would presumably need to be defined first by case category, then by priority    
    """    
    magnitude = IntegerProperty()
    description = StringProperty()
    def __unicode__(self):
        return "%d" % (self.magnitude)

    @staticmethod
    def High():
        return Priority(magnitude=1, description="High")
    #etc etc

    class Meta:
        app_label = 'casetracker'
        #verbose_name = "Priority Type"
        #verbose_name_plural = "Priority Types"
        #ordering = ['magnitude']

class Status (Document):
    """
    Status is the model to capture the different states of a case.
    In Fogbugz, these are also classified within the category of the original bug.
    ie, a bug's status states will be fundamentally different from a Feature or Question.
    """    
    display = StringProperty(required=True) #from description
    state_class = StringProperty(required=True)
    
    #query filters can be implemented a la kwarg evaluation:
    #http://stackoverflow.com/questions/310732/in-django-how-does-one-filter-a-queryset-with-dynamic-field-lookups/659419#659419        
    #Note: 
    #fogbugz had a bunch of classifiers here that describe the nature of the status
    #in other words they should still fall within the 4 main  classifiers of status:
    #resolved, duplicate, deleted, done?
    def __unicode__(self):
        return "Status: %s" % (self.display)


    @staticmethod
    def Open():
        return Status(display='Open', state_class='OPEN')

    @staticmethod
    def Closed():
        return Status(display='Closed', state_class='CLOSED')
    
    @staticmethod
    def Resolved():
        return Status(display='Resolved', state_class='RESOLVED')
    

    #etc, etc.

    class Meta:
        app_label = 'casetracker'
        #verbose_name = "Case Status Type"
        #verbose_name_plural = "Case Status Types"
        #ordering = ['display']
    


class ActivityClass(Document):
    """
    An ActivityClass describes sanction-able actions that can be done revolving around a case.
    The hope for this as these are models, are that distinct functional actions can be modeled around these
    
    These are SPECIFIC to the category that they are a part of.  
    Event Activities.
    
    For example:
    edit case
    email
    make a phone call
    sms         
    """
    slug = StringProperty(required=True) #from name
    #past_tense = StringProperty(max_length=64, help_text = "The past tense description of this activity") #from phrasing
    #active_tense = StringProperty(max_length=64, help_text = "The active tense of this activity - this text will be displayed as a button in the case view.") #present as button on case view
    event_class = StringProperty(required=True) # what class of event is it?

    ######################
    #target_status is currently unused (3/17/2010), however there may come a time for events to be totally manage
    #via the DB, so this field is being kept live in the model even though it has no use at the moment.
    #target_status = models.ForeignKey("Status", blank=True, null=True,
                                      #help_text=_("This event activity may alter the case's status.  If it does, it must exist here.",
                                    #related_name="set_by_activities"))
#    CASE_EVENT_CHOICES = (
#        (constants.CASE_EVENT_OPEN, 'Open/Create'), #case state
#        (constants.CASE_EVENT_VIEW, 'View'),
#        (constants.CASE_EVENT_EDIT, 'Edit'),
#        (constants.CASE_EVENT_WORKING, 'Working'), #working on case?  this seems a bit ridiculous
#        (constants.CASE_EVENT_REOPEN, 'Reopen'), #case state
#        (constants.CASE_EVENT_COMMENT, 'Comment'),
#        (constants.CASE_EVENT_CUSTOM, 'Custom'), #custom are activities that don't resolve around the basic open/edit/view/resolve/close
#        (constants.CASE_EVENT_RESOLVE, 'Resolve'), #case status state
#        (constants.CASE_EVENT_CLOSE, 'Close'), #case status state
#    )
    @staticmethod
    def Open():
        return ActivityClass(slug='open', event_class=CASE_EVENT_CHOICES[0][0])

    @staticmethod
    def Edit():
        return ActivityClass(slug='edit', event_class=CASE_EVENT_CHOICES[2][0])

    def __unicode__(self):
        return "[%s] Activity" % (self.slug)

    class Meta:
        app_label = 'casetracker'
        #verbose_name = "Case Event Activity Type"
        #verbose_name_plural = "Case Event Activity Types"        
        #ordering=['event_class', 'slug']


class CaseEvent(Document):
    """
    A CaseEvent is any action done revolving around a case.
    A Interaction in our book is an actual medical document that happens for a particular medical document/domain.
    
    An encounter in this scope is an action that happens and is resolved around a particular case.
    
    It is meant to capture outside the scope of the case table itself, the actions and their accompanying
    examples of what happened to a case.
    """
    event_id = StringProperty(default=make_uuid, required=True) #universal id even though this is embedded within a case.
    notes = StringProperty()
    activity = SchemaProperty(ActivityClass)
    created_date = DateTimeProperty(required=True)
    created_by = StringProperty(required=True)
    parent_event = StringProperty() #the parent event_id of this guy, say this is a reply to a thread within this.

    def save(self):
        if self.event_id == None:
            self.event_id = uuid.uuid1().hex
        if self.created_by == None:
            raise Exception("Missing fields in Case creation - created by")           
        if self.created_date == None:     
            self.created_date = datetime.utcnow()            
        super(CaseEvent, self).save()  
    
    def __unicode__(self):
        return "Event (%s} by %s on %s" % (self.activity.slug, self.created_by.title(), self.created_date.strftime("%I:%M%p %Z %m/%d/%Y"))
    
    class Meta:
        app_label = 'casetracker'
        #verbose_name = "Case Event"
        #verbose_name_plural = "Case Events"
        #ordering = ['-created_date']


class Case(Document):
    """
    A case in this system is the actual even that needs due diligence and subsequent closure.
    
    These are finite and discrete tasks that must be done.  Linking these cases to someone or something
    must be implemented elsewhere.

    all _by fields (opened_by, created_by, etc. should map back to an Actor uuid)
    
    """
    description = StringProperty(required=True)
    orig_description = StringProperty()
    base_type = StringProperty(default="Case") #for subclassing this needs to stay consistent

    status=SchemaProperty(Status)
    patient = StringProperty() #Patient uuid from patient app

    body = StringProperty(required=True)
    
    priority = SchemaProperty(Priority)
    
    opened_date = DateTimeProperty(required=True)
    opened_by = StringProperty(required=True)
    
    assigned_to = StringProperty(required=True)
    assigned_date = DateTimeProperty(required=True)
    
    last_edit_date = DateTimeProperty(required = True)
    last_edit_by = StringProperty(required=True)

    resolved_date = DateTimeProperty()
    resolved_by = StringProperty()

    closed_date = DateTimeProperty()
    closed_by = StringProperty()

    due_date = DateTimeProperty()
    
    events = SchemaListProperty(CaseEvent)
    parent_case = StringProperty()


    @classmethod
    def create(cls, actor_creator, description, body, created_date=None, priority=None, assigned_to=None, status=None):
        instance = cls()
        instance.opened_by = actor_creator.id
        if created_date == None:
            instance.opened_date = datetime.utcnow()
        else:
            instance.opened_date = created_date

        instance.description = description
        instance.orig_description = description
        instance.body = body
        if priority == None:
            instance.priority = Priority.High()
        else:
            instance.priority = priority
        if assigned_to == None:
            instance.assigned_to = actor_creator.id
        else:
            instance.assigned_to = assigned_to.id

        if status==None:
            instance.status=Status.Open()
        else:
            instance.status = status

        instance.last_edit_by = instance.opened_by
        instance.last_edit_date = instance.opened_date

        instance.assigned_date = datetime.utcnow()
        instance.save()
        return instance


    def get_absolute_url(self):
        #return "/case/%s" % self.id
        return reverse('manage_case', kwargs={'case_id': self.i})
    
    @property
    def is_active(self):
        if self.status.state_class == constants.CASE_STATE_OPEN:
            return True
        else:
            return False 
    
    @property
    def is_resolved(self):
        if self.status.state_class == constants.CASE_STATE_RESOLVED or self.status.state_class == constants.CASE_STATE_CLOSED:
            return True
        else:
            return False
    
    @property
    def is_closed(self):
        if self.status.state_class == constants.CASE_STATE_CLOSED:
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
    
    @property
    def child_cases(self):
        sub_ids = Case.view('casetracker/subcases', key=self._id).all()
        return sub_ids
                
    
    def add_event(self, event, do_save=False):
        """Append a case event to a case's history of things        
        """
        #do some error checking?
        self.events.append(event)
        if do_save:
            super(Case, self).save()
    
    
    def save(self, edit_date=None):
        """
        Save a case.  Apply additional post save signaling here.       
        """
        if edit_date == None:
            event_created_date = datetime.utcnow()
        else:
            event_created_date = edit_date

        if self._id == None:
            #it's a brand new case, we can set the activity here.
            if self.opened_by  == None:
                raise Exception("Error, you must set a creator for this case to save")
            if self.opened_date == None:
                self.opened_date = datetime.utcnow()
            self.status = Status.Open()
            edit_event = CaseEvent(notes = "Case created",
                               activity = ActivityClass.Open(),
                               created_by = self.last_edit_by,
                               created_date=event_created_date)

        else:
            if self.last_edit_by == None:
                raise Exception("Missing fields in edited Case: last_edit_by")
            
            #create a case event to indicate a save/edit happened.

            edit_event = CaseEvent(notes = "Case edited",
                                   activity = ActivityClass.Edit(),
                                   created_by = self.last_edit_by,
                                   created_date=event_created_date)

        self.add_event(edit_event, do_save=False)
        if edit_date == None:
            self.last_edit_date = datetime.utcnow()
        else:
            self.last_edit_date = edit_date 
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
        #verbose_name = "Case"
        #verbose_name_plural = "Cases"
        #ordering = ['-opened_date']
    
#
#class Follow(models.Model):
#    """
#    Simple model for a user to follow a particular case
#    """
#    id = StringProperty(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
#    case = models.ForeignKey(Case, null=True, blank=True, related_name="messages")   #is this message related to a particular case?
#    is_public = models.BooleanField(default=False)
#    author = models.ForeignKey(Actor, related_name='messages_authored')
    
class HomeMonitoringCase(Case):
    device_id = StringProperty()

    class Meta:
        app_label='casetracker'


class XFormCase(Case):
    class Meta:
        app_label='casetracker'

class ScheduleCase(Case):
    recurring = BooleanProperty()
    start_date = DateTimeProperty()
    end_date = DateTimeProperty()
    frequency = StringProperty()

    class Meta:
        app_label='casetracker'


