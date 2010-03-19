from itertools import chain

import logging
from django.db import models

from django.db.models import Q
from django.contrib.auth.models import User

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from datetime import datetime, timedelta
from middleware import threadlocals

from django.core.urlresolvers import reverse
import uuid
from django.utils.translation import ugettext_lazy as _

import constants as constants
#from casetracker.CategoryHandler import CategoryHandlerBase, DefaultCategoryHandler



#from django.db.models.fields.related import RelatedManager, ManyRelatedManager


def make_uuid():
    return uuid.uuid1().hex



CASE_EVENT_CHOICES = (
        (constants.CASE_EVENT_OPEN, 'Open/Create'), #case statust state
        (constants.CASE_EVENT_VIEW, 'View'),
        (constants.CASE_EVENT_EDIT, 'Edit'),
        (constants.CASE_EVENT_WORKING, 'Working'), #working on case?  this seems a bit ridiculous                
        (constants.CASE_EVENT_REOPEN, 'Reopen'), #case state
        (constants.CASE_EVENT_COMMENT, 'Comment'),
        (constants.CASE_EVENT_CUSTOM, 'Custom'), #custom are activites that don't resolve around the basic open/edit/view/resolve/close
        
        (constants.CASE_EVENT_RESOLVE, 'Resolve'), #case status state
        (constants.CASE_EVENT_CLOSE, 'Close'), #case status state
    )

#ok, this is a bit nasty, but the rationale is, an actual CASE only really has 3 states. open, resolved and closed
#the case_state_chjocies are acutal events that happen AROUND a case, that can alter the state of a case.


CASE_STATES = (
        (constants.CASE_STATE_OPEN, 'Open/Active'),
        (constants.CASE_STATE_RESOLVED, 'Resolved'),
        (constants.CASE_STATE_CLOSED, 'Closed'),
)

    
class Category(models.Model):
    """
    The Category is the central piece of the casetracker model tree.
    
    All cases must embody a certain category.
    
    A category then is the bridge between the existence of a case in the database and how it is handled between the database
    and other types within pythonland.
    
    So, in ashand, you define different cases as different classes of "case-able" information.
    So, a case can be an issue, question, or alerts from some therapeutic monitor or scheduling - the list goes on.
    
    To keep the purity of the casetracker app, other models that wish to add itself to the casetracker.
    
    Simple setups will be:
    Question
    Issue    
    
    Schedule Item    
        Appointment
        Order
        Prescription    
    """
    id = models.CharField(_('Unique id'), max_length=32, unique=True, default=make_uuid, primary_key=True) #primary_key override?
    slug = models.SlugField(unique=True) #from category
    display = models.CharField(max_length=64)
    plural = models.CharField(max_length=32)    
    #deprecated = models.BooleanField()
    #version = models.PositiveIntegerField()
    #parent_version = models.ForeignKey("self")
    default_status = models.ForeignKey("Status", blank=True, null=True, related_name="Default Status") #this circular is nullable in FB
    
    bridge_module = models.CharField(max_length=128, blank=True, null=True,
                                      help_text=_("This is the fully qualified name of the module that implements the MVC framework for case lifecycle management."))
    
    bridge_class = models.CharField(max_length=64, blank=True, null=True,
                                     help_text=_('This is the actual class name of the subclass of the CategoryHandler you want to handle this category of case.'))
    
    
    @property
    def bridge(self): #from handler
        """
        Returns the class instance of the category CategoryHandler.  If none is defined, return the DefaultCategoryHandler
        """
        #nasty hack here, but due to prevent circular refernces, we need to make sure it's not referenced until necessary
        from casetracker.caseregistry import CategoryBridge, ActivityBridge
        handler = None
        if not hasattr(self, '_bridge'):            
            if self.bridge_module == None or self.bridge_class == None:
                raise Exception("Error, invalid configuration, this category has no bridge class defined")
            else:                            
                try:
                    hmod = __import__(self.bridge_module, {}, {}, [''])                    
                    if hasattr(hmod, self.bridge_class):
                        hclass = getattr(hmod, self.bridge_class)
                        if issubclass(hclass, CategoryBridge):
                            handler = hclass()                                                                 
                except Exception, e:
                    logging.error("Unable to import the handler class for category %s: %s" % (self.category, e))
                
                if handler == None:
                    raise Exception("Error, invalid configuration, this category has no bridge class defined")
            self._bridge = handler        
        return self._bridge
        
        
    
    def __unicode__(self):
        return "%s" % (self.slug)
    class Meta:
        verbose_name = "Category Type"
        verbose_name_plural = "Category Types"



class CaseAction(models.Model):
    """
    A case action is a descriptor for capturing the types of actions you can actuate upon a case.
    These are linked to a case to describe the desired NEXT action to take upon a case.
    
    In this case, we want to be able to capture the differing types of 'todo for next time' actions you 
    can assign to a case.
    
    The main desired actions are
    Follow up w/ subject: A date bound action that says I should follow up with the patient
    To Resolve: A date bound action that says I should finish said case by the next_action_date - which effectively becomes a due date.
    
    These should be universal across all categories.
    """
    description = models.CharField(max_length=64)
    def __unicode__(self):
        return "%s" % (self.description)
    
    class Meta:
        verbose_name = "Case Action Type"
        verbose_name_plural = "Case Action Types"


    
class Priority(models.Model):
    """
    Priorities are assigned on a case basis, and are universally assigned.
    Sorting would presumably need to be defined first by case category, then by priority    
    """    
    magnitude = models.IntegerField()
    description = models.CharField(max_length=32)
    default = models.BooleanField()    
    def __unicode__(self):
        return "%d" % (self.magnitude)

    class Meta:
        verbose_name = "Priority Type"
        verbose_name_plural = "Priority Types"


class StatusActivities(models.Model):
    """
    ManyToMany linkage of Status and the activities that are allowable from that case state.
    
    Hopefully with this through model being here, more enforcement and/model define-able state information
    can be recorded and be database  
    """    
    status = models.ForeignKey("Status", related_name='legal_activities_list')
    legal_activity = models.ForeignKey("EventActivity", related_name="legal_for_status")
    
    class Meta:
        unique_together=('status','legal_activity')

class Status (models.Model):
    """
    Status is the model to capture the different states of a case.
    In Fogbugz, these are also classified within the category of the original bug.
    ie, a bug's status states will be fundamentally different from a Feature or Question.
    """    
    id = models.CharField(_('Unique id'), max_length=32, unique=True, default=make_uuid, primary_key=True) #primary_key override?
    slug = models.SlugField(unique=True)
    display = models.CharField(max_length=64) #from description
    
    category = models.ForeignKey(Category, related_name='category_states')
    state_class = models.TextField(max_length=24, choices=CASE_STATES)
    

    ##this should have a limit choices to for self.category, but that's a nasty hack.
    #allowable_actions = models.ManyToManyField("EventActivity", through="StatusActivityLink", related_name='legal_action_for_states') 
    @property
    def allowable_actions(self):
        if not hasattr(self, '_allowable_actions'):            
            legal_activities = StatusActivities.objects.select_related().filter(status=self).values_list('legal_activity',flat=True)
            self._allowable_actions = EventActivity.objects.select_related().filter(id__in=legal_activities)        
        return self._allowable_actions
    
    def set_activity(self, event_activity):
        try:
            slink = StatusActivities(status=self, legal_activity=event_activity)
            slink.save()
        except Exception, e:
            raise Exception("Error, an event activity can only be registered once to a given state" + str(e))
    
    
    #query filters can be implemented a la kwarg evaluation:
    #http://stackoverflow.com/questions/310732/in-django-how-does-one-filter-a-queryset-with-dynamic-field-lookups/659419#659419        
    #Note: 
    #fogbugz had a bunch of classifiers here that describe the nature of the status
    #in other words they should still fall within the 4 main  classifiers of status:
    #resolved, duplicate, deleted, done?
    def __unicode__(self):
        return "%s: %s" % (self.category.slug, self.display)

    class Meta:
        verbose_name = "Case Status Type"
        verbose_name_plural = "Case Status Types"
        ordering = ['category', 'id']
    


class EventActivity(models.Model):
    """
    An Event Activity describes sanction-able actions that can be done revolving around a case.
    The hope for this as these are models, are that distinct functional actions can be modeled around these
    
    These are SPECIFIC to the category that they are a part of.  
    Event Activities.
    
    For example:
    edit case
    
    email
    make a phone call
    sms         
    """
    id = models.CharField(_('Unique id'), max_length=32, unique=True, default=make_uuid, primary_key=True) #primary_key override?
    slug = models.SlugField(unique=True) #from name
    past_tense = models.CharField(max_length=64) #from phrasing
    active_tense = models.CharField(max_length=64) #present as button on case view    
    event_class = models.TextField(max_length=32, choices=CASE_EVENT_CHOICES) # what class of event is it?
    category = models.ForeignKey(Category, related_name='category_activities') # different categories have different event types    
    summary = models.CharField(max_length=255)    

    ######################
    #target_status is currently unused (3/17/2010), however there may come a time for events to be totally manage
    #via the DB, so this field is being kept live in the model even though it has no use at the moment.
    target_status = models.ForeignKey("Status", blank=True, null=True, 
                                      help_text = _("This event activity may alter the case's status.  If it does, it must exist here.",
                                    related_name="set_by_activities"))
    

    
    bridge_module = models.CharField(max_length=128, blank=True, null=True,
                                      help_text=_("This is the fully qualified name of the module that implements the MVC framework for case lifecycle management."))
    
    bridge_class = models.CharField(max_length=64, blank=True, null=True,
                                     help_text=_('This is the actual class name of the subclass of the CategoryHandler you want to handle this category of case.'))
  
    
    def __unicode__(self):
        return "(%s) [%s] Activity" % (self.category, self.slug)

    class Meta:
        verbose_name = "Case Event Activity Type"
        verbose_name_plural = "Case Event Activity Types"        
   
    @property
    def bridge(self): #from handler
        """
        Returns the class instance of the category CategoryHandler.  If none is defined, return the DefaultCategoryHandler
        """
        handler = None
        from casetracker.caseregistry import ActivityBridge
        if not hasattr(self, '_bridge'):
            if self.bridge_module == None or self.bridge_class == None:
                raise Exception("Error, invalid configuration, this category has no bridge class defined")
            else:                            
                try:
                    hmod = __import__(self.bridge_module, {}, {}, [''])
                    if hasattr(hmod, self.bridge_class):
                        hclass = getattr(hmod, self.bridge_class)
                        if issubclass(hclass, ActivityBridge):
                            handler = hclass()                                                                 
                except Exception, e:
                    logging.error("Unable to import the handler class for category %s: %s" % (self.category, e))
                
                if handler == None:
                    raise Exception("Error, invalid configuration, this category has no bridge class defined")
            self._bridge = handler        
        return self._bridge


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
    
    activity = models.ForeignKey(EventActivity)
    
    created_date = models.DateTimeField()
    created_by = models.ForeignKey(User)        
    
    def save(self, unsafe=False):
        if unsafe:
            self.id = uuid.uuid1().hex
            super(CaseEvent, self).save()
            return
            
        if self.created_date == None:     
            if self.created_by == None:
                raise Exception("Missing fields in Case creation - created by")           
            self.created_date = datetime.utcnow()                            
            self.id = uuid.uuid1().hex
        super(CaseEvent, self).save()  
    
    def __unicode__(self):
        return "Event (%s} by %s on %s" % (self.activity.slug, self.created_by.get_full_name(), self.created_date.strftime("%I:%M%p %Z %m/%d/%Y"))
    
    class Meta:
        verbose_name = "Case Event"
        verbose_name_plural = "Case Events"
        ordering = ['-created_date']

class CaseTag(models.Model):
    case = models.ForeignKey("Case", related_name="tagged_case_objects")
    
    #generic linkage to arbitrary objects
    object_type = models.ForeignKey(ContentType, verbose_name='Case linking content type', blank=True, null=True)
    object_uuid = models.CharField('object_uuid', max_length=32, db_index=True, blank=True, null=True)
    content_object = generic.GenericForeignKey('object_type', 'object_uuid')
   

class Case(models.Model):
    """
    A case in this system is the actual even that needs due diligence and subsequent closure.
    
    These are finite and discrete tasks that must be done.  Linking these cases to someone or something
    must be implemented elsewhere. 
    
    The scope of these cases are currently attached to the actual agents that need to work on them.
    
    Changes to these cases will be managed by django-reversion.  Actions revolving around these cases will be done via encounters.
    
    The uuid should be the primary key, but for the synchronization framework, having a uuid key do all the queries
    and potentially be the primary key should be a top priority.    
    """    
    id = models.CharField(_('Case Unique id'), max_length=32, unique=True, default=make_uuid, primary_key=True) #primary_key override?
    
    description = models.CharField(max_length=160)
    orig_description = models.CharField(max_length=160, blank=True, null=True, editable=False)    
    
    category = models.ForeignKey(Category)
    status = models.ForeignKey(Status)    
    
    body = models.TextField(blank=True, null=True)
        
    
    priority = models.ForeignKey(Priority)
    
    
    
    opened_date = models.DateTimeField()
    opened_by = models.ForeignKey(User, related_name="case_opened_by")
    
    last_edit_date = models.DateTimeField(null=True, blank=True)
    last_edit_by = models.ForeignKey(User, related_name="case_last_edit_by", null=True, blank=True) 
        
    #next_action_date = models.DateTimeField(null=True, blank=True)
    #next_action = models.ForeignKey(CaseAction, null=True)
    
    resolved_date = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, related_name="case_resolved_by", null=True, blank=True)
        
    closed_date = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(User, related_name="case_closed_by", null=True, blank=True)    
    
    assigned_to = models.ForeignKey(User, related_name="case_assigned_to", null=True, blank=True)   
    assigned_date = models.DateTimeField(null=True, blank=True)
    
    parent_case = models.ForeignKey('self', null=True, blank=True, related_name='child_cases')
    
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
                
    def save(self, activity=None, save_comment=None, unsafe=False):
        """
        Save a case.
        
        There are two ways to save a case.
        If activity is None, then it implies that this is a NEW case.        
        If that's saved, then an EventActivity that does a basic OPEN will be saved.
        
        If activity != None, then this implies that a structured activity did changes to the case.
        
        The unsafe flag is only for unit testing to alter properties of the datetimes and such.        
        """
        if unsafe:
            if self.opened_date == None:
                logging.warning("Case save unsafe: no opened date set")            
            if self.opened_by == None:
                logging.warning("Case save unsafe: no opened by set")
            if self.last_edit_date == None:
                logging.warning("Case save unsafe: no last edit date set")
            if self.last_edit_by == None:
                logging.warning("Case save unsafe: no last edit by set")
    
            super(Case, self).save()
            return
                
        #NEW CASE
        if self.opened_date == None: #this is a bit hackish, with the overriden id, the null ID is hard to verify.  so, we should verify it by the null opened_date
            if self.opened_by == None or self.description == None:
                raise Exception("Missing fields in Case creation - opened by and description")            
            
            #if we're brand new, we'll update the dates in this way:
            self.opened_date = datetime.utcnow()
            self.last_edit_date = self.opened_date #this causes some issues with the basic queries, so we will set it to be the same as opened date
            self.last_edit_by = self.opened_by
            self.orig_description = self.description            
        else:
            #EXISTING CASE
            if activity == None:
                raise Exception("Error, you must set an EventActivity for this Case Save")
            else:
                self.event_activity = activity
            if save_comment != None:
                self.save_comment = save_comment
            
            
            if self.last_edit_by == None:
                raise Exception("Missing fields in Case edit - last_edit_by")
                        
            #now, we need to check the status change being done to this.            
            state_class = self.status.state_class
            if state_class == constants.CASE_STATE_RESOLVED: #from choices of CASE_STATES
                if self.resolved_by == None:
                    raise Exception("Case state is now resolved, you must set a resolved_by")
                else:
                    self.resolved_date = datetime.utcnow()
            elif state_class == constants.CASE_STATE_CLOSED:
                if self.closed_by == None:
                    raise Exception("Case state is now resolved, you must set a resolved_by")
                else:
                    #ok, closed by is set, let's double check that it's been resolved
                    if self.resolved_by == None:
                        raise Exception("Error, this case must be resolved before it can be closed")
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
        verbose_name = "Case"
        verbose_name_plural = "Cases"
        ordering = ['-opened_date']


class Filter(models.Model):
    """
    
    """

    #below are the enumerated integer choices because integer fields don't like choices that aren't ints.
    #for more information see here:
    #http://www.b-list.org/weblog/2007/nov/02/handle-choices-right-way/
    TODAY = 0
    ONE_DAY = 1
    THREE_DAYS = 3
    ONE_WEEK = 7
    TWO_WEEKS = 14
    ONE_MONTH = 30
    TWO_MONTHS = 60
    THREE_MONTHS = 90
    SIX_MONTHS = 180
    ONE_YEAR = 365
    
    TIME_DURATION_FUTURE_CHOICES = (
        (-ONE_DAY, 'In the past'),
        (TODAY, 'Today'),
        (ONE_DAY, 'Today or tomorrow'),
        (THREE_DAYS, 'In the next three days'),
        (ONE_WEEK, 'In the next week'),
        (TWO_WEEKS, 'In the next two weeks'),
        (ONE_MONTH, 'In the next month'),
        (TWO_MONTHS, 'In the next two months'),
        (THREE_MONTHS, 'In the next three months'),
        (SIX_MONTHS, 'In the next six months'),
        (ONE_YEAR, 'In the next year'),
    )
    
    TIME_DURATION_PAST_CHOICES = (
        (TODAY, 'Today'),
        (-ONE_DAY, 'Yesterday or today'),
        (-ONE_WEEK, 'In the past week'),
        (-ONE_MONTH, 'In the past month'),
        (-TWO_MONTHS, 'In the past two months'),
        (-THREE_MONTHS, 'In the past three months'),
        (-SIX_MONTHS, 'In the past six months'),
        (-ONE_YEAR, 'In the past year'),
    )
    #metadata about the query
    description = models.CharField(max_length=64)
    creator = models.ForeignKey(User, related_name="filter_creator")
    shared = models.BooleanField(default=False)
    
    #case related properties
    category = models.ForeignKey(Category, null=True, blank=True)
    status = models.ForeignKey(Status, null=True, blank=True)
    priority = models.ForeignKey(Priority, null=True, blank=True)
    
    assigned_to = models.ForeignKey(User, null=True, blank=True, related_name="filter_assigned_to")
    opened_by = models.ForeignKey(User, null=True, blank=True, related_name="filter_opened_by")
    last_edit_by = models.ForeignKey(User, null=True, blank=True, related_name="filter_last_edit_by")    
    resolved_by = models.ForeignKey(User, null=True, blank=True, related_name="filter_resolved_by")
    closed_by = models.ForeignKey(User, null=True, blank=True, related_name="filter_closed_by")
        
    opened_date = models.IntegerField(choices=TIME_DURATION_PAST_CHOICES, null=True, blank=True)
    last_edit_date = models.IntegerField(choices=TIME_DURATION_PAST_CHOICES, null=True, blank=True)
    resolved_date = models.IntegerField(choices=TIME_DURATION_PAST_CHOICES, null=True, blank=True)
    closed_date = models.IntegerField(choices=TIME_DURATION_PAST_CHOICES, null=True, blank=True)
    
    next_action_date = models.IntegerField(choices=TIME_DURATION_FUTURE_CHOICES, null=True, blank=True)    
    
    #case Event information
    last_event_type = models.ForeignKey(EventActivity, null=True, blank=True)
    last_event_date = models.IntegerField(choices=TIME_DURATION_PAST_CHOICES, null=True, blank=True)
    last_event_by = models.ForeignKey(User, null=True, blank=True)
    
        
    #this should come in as a dictionary of key-value pairs that are compatible with a 
    #django query when resolved as a kwargs.
    #http://stackoverflow.com/questions/310732/in-django-how-does-one-filter-a-queryset-with-dynamic-field-lookups
    #http://stackoverflow.com/questions/353489/cleaner-way-to-query-on-a-dynamic-number-of-columns-in-django
       
    def get_filter_queryset(self):
        """
        On a given filter instance, we will generate a query set by applying all the FKs as query objects
        
        The return value is a queryset after applying all the query filters and doing a filter with 
        the case events as well.
        """        
        utcnow = datetime.utcnow()
                
        case_query_arr = []        
        case_event_query_arr = []

        
        if self.category:
            case_query_arr.append(Q(category=self.category))        
        if self.status:
            case_query_arr.append(Q(status=self.status))
        if self.priority:
            case_query_arr.append(Q(priority=self.priority))
        if self.assigned_to:            
            if self.assigned_to.id == 1: #this is a hackish way of saying it's the reflexive user
                #run the query with the threadlocals current user                
                case_query_arr.append(Q(assigned_to=threadlocals.get_current_user()))
            else:
                case_query_arr.append(Q(assigned_to=self.assigned_to))        
        if self.opened_by:
            if self.opened_by.id == 1: #this is a hackish way of saying it's the reflexive user
                #run the query with the threadlocals current user
                case_query_arr.append(Q(opened_by=threadlocals.get_current_user()))
            else:
                case_query_arr.append(Q(opened_by=self.opened_by))            
        if self.last_edit_by:
            if self.last_edit_by.id == 1: #this is a hackish way of saying it's the reflexive user
                #run the query with the threadlocals current user
                case_query_arr.append(Q(last_edit_by=threadlocals.get_current_user()))
            else:
                case_query_arr.append(Q(last_edit_by=self.last_edit_by))
        if self.resolved_by:
            if self.resolved_by.id == 1: #this is a hackish way of saying it's the reflexive user
                #run the query with the threadlocals current user
                case_query_arr.append(Q(resolved_by=threadlocals.get_current_user()))
            else:
                case_query_arr.append(Q(resolved_by=self.resolved_by))            
        if self.closed_by:
            if self.closed_by.id == 1: #this is a hackish way of saying it's the reflexive user
                #run the query with the threadlocals current user
                case_query_arr.append(Q(closed_by=threadlocals.get_current_user()))
            else:
                case_query_arr.append(Q(closed_by=self.closed_by))        
                
                
        if self.opened_date:
            compare_date = utcnow + timedelta(days=self.opened_date)
            case_query_arr.append(Q(opened_date__gte=compare_date))
        if self.last_edit_date:
            compare_date = utcnow + timedelta(days=self.last_edit_date)
            case_query_arr.append(Q(last_edit_date__gte=compare_date))
        if self.resolved_date:
            compare_date = utcnow + timedelta(days=self.resolved_date)
            case_query_arr.append(Q(resolved_date__gte=compare_date))
        if self.closed_date:
            compare_date = utcnow + timedelta(days=self.closed_date)
            case_query_arr.append(Q(closed_date__gte=compare_date))
        
        
        if self.next_action_date:
            compare_date = utcnow + timedelta(days=self.next_action_date)
            case_query_arr.append(Q(next_action_date__lte=compare_date))
                             
        
        #ok, this is getting a little tricky.
        #query CaseEvent and we will get the actual cases.  we will get the id's of the cases and apply
        #those back as a filter
        if self.last_event_type:
            case_event_query_arr.append(Q(activity=self.last_event_type))
        if self.last_event_by:
            if self.last_event_by.id == 1: #this is a hackish way of saying it's the reflexive user
                #run the query with the threadlocals current user
                case_event_query_arr.append(Q(created_by=threadlocals.get_current_user()))
            else:
                case_event_query_arr.append(Q(created_by=self.last_event_by))            
            
        if self.last_event_date:        
            compare_date = utcnow + timedelta(days=self.last_event_date)
            case_event_query_arr.append(Q(created_date__gte=self.last_event_date))            

        #now, we got the queries built up, let's run the queries                
        cases = Case.objects.select_related('opened_by', 'last_edit_by', 'resolved_by', 'closed_by', 'assigned_to', 'status', 'category', 'priority', 'carteam_set').all()        
        for qu in case_query_arr:
            #dmyung 12-8-2009
            #doing the filters iteratively doesn't seem to be the best way.  there ought to be a way to chain
            #them all in an evaluation to the filter() call a-la the kwargs or something.  since these
            # are ANDED, we want them to be done sequentially (ie, filter(q1,q2,q3...)
            #negations should be handled by the custom search            
            cases = cases.filter(qu)
        
        if len(case_event_query_arr) > 0:            
            case_events = CaseEvent.objects.select_related().all()                  
            for qe in case_event_query_arr:
                case_events = case_events.filter(qe)
            
            #get all the case ids from the case event filters
            case_events_cases_ids = case_events.values_list('case', flat=True)        
            
            if len(case_events_cases_ids) > 0:
                cases = cases.filter(pk__in=case_events_cases_ids)
                            
        return cases
        
    def __unicode__(self):
        return "Filter - %s" % (self.description)
    
    class Meta:
        verbose_name = "Case Filter"
        verbose_name_plural = "Case Filters"


class GridColumn(models.Model):
    """
    The gridcolumn is the main, flat store for all columns that could be used in a grid.
    
    It's flat, the name of the column is directly used in the Case column selector and sort criteria.
    So there's no need for namespacing it or anything like that.  If it's named something, it'll exist here.
    
    In other words, the GridColumn's name MUST be a property of case and casefilter for it to be useful.
    
    """
    name = models.CharField(max_length=32)
    def __unicode__(self):
        return self.name


class GridSort(models.Model):
    """
    When a grid preference FKs to a GridColumn, this through model will tell how to represent it
    when using the column as a sorting column.  In representation it'll be either be name or -name.
    
    The gridcolumn presents the actual case property of the Case queryset you pass into the ordering() method.
    The filter queryset will be built using these strings.
    """
    column = models.ForeignKey("GridColumn", related_name='gridcolumn_sort')
    preference = models.ForeignKey("GridPreference", related_name="gridpreference_sort")
    ascending = models.BooleanField()
    order = models.PositiveIntegerField()
    @property
    def sort_display(self):
        if self.ascending:
            return self.column.name
        else:
            return "-%s" % self.column.name
    def __unicode__(self):
        if self.ascending:
            ascend = "ascending"
        else:
            ascend = "descending"
        return "GridSort - %s %s" % (self.column, ascend)
    
    class Meta:
        verbose_name = "Grid column sort ordering"
        verbose_name_plural = "Grid column sort order definitions"
        ordering = ['order']
    

class GridOrder (models.Model):
    """
    When a grid preference FKs to a GridColumn, this through model will tell how to represent it
    when using the column as a column for display.  This tells us which columns will be arranged in what order
    for display on the data table.
    
    The gridcolumn presents the actual Case queryset properties to actually render in the order they are reprsented
    in this through model.
    """
    column = models.ForeignKey("GridColumn", related_name='gridcolumn_displayorder')
    preference = models.ForeignKey("GridPreference", related_name="gridpreference_displayorder")
    order = models.PositiveIntegerField()
    
    class Meta:
        verbose_name = "Grid column display ordering"
        verbose_name_plural = "Grid column display order definitions"
        ordering = ['order']
    

class GridPreference(models.Model):
    """
    A filter will have a one to one mapping to this model for showing how to display the given grid.    
    """
    filter = models.OneToOneField(Filter, related_name='gridpreference') #this could be just a foreign key and have multiple preferences to a given filter.
    
    display_columns = models.ManyToManyField(GridColumn, through=GridOrder, related_name="display_columns")
    sort_columns = models.ManyToManyField(GridColumn, through=GridSort, related_name="sort_columns")
    
    
    
    def __unicode__(self):
        return "Grid Display Preference: %s" % self.filter.description    
    
    class Meta:
        verbose_name = "Filter Grid Display Preference"
        verbose_name_plural = "Filter Grid Display Preferences"
        ordering = ['filter']
        
    @property
    def get_display_columns(self):
        """
        returns the display columns in order of the through class's definition
        """
        col_orders = self.gridpreference_displayorder.all().values_list('column__id', flat=True)
        return GridColumn.objects.all().filter(id__in=col_orders)
    
    @property
    def get_sort_columns(self):
        """
        returns the display columns in order of the through class's definition
        """
        col_sort_orders = self.gridpreference_sort.all().values_list('column__id', flat=True)
        return GridColumn.objects.all().filter(id__in=col_sort_orders)    
    
    @property
    def get_colsort_jsonarray(self):
        #"aaSorting": [ [0,'asc'], [1,'asc'] ],
        if not hasattr(self, '_sort_json'):                
            cols = list(self.get_display_columns)
            sorts = self.gridpreference_sort.all()
            ret = []
            for s in sorts:
                idx = cols.index(s.column)
                if s.ascending == 1:
                    ret.append([idx + 1, 'asc'])
                else:
                    ret.append([idx + 1, 'desc'])
            
            self._sort_json = ret        
        return self._sort_json
    

#class Message(models.Model):    
#    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
#    subject = models.CharField(max_length=255)
#    case = models.ForeignKey(Case, null=True, blank=True, related_name="messages")   #is this message related to a particular case?    
#    is_public = models.BooleanField(default=False)    
#    body = models.TextField()
#    
#    author = models.ForeignKey(User, related_name='messages_authored')
#    recipients = models.ManyToManyField(User, related_name='messages_received') #straight recipients, no bcc's here
#    
#    #cased = generic.GenericRelation(TaggedItem)
#    parent_message = models.ForeignKey('self', related_name='replies')
#    
#    
#    
#    def can_read(self, user):
#        """
#        Can the given User object read this message? This depends on the public flag, and authorship
#        """         
#        if self.is_public:
#            return True
#        else:
#            if self.author == user or self.recipients.all().filter(id=user.id):
#                return True
#            else:
#                return False

#
#class Reminder(models.Model):
#    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
#    case = models.ForeignKey(Case, null=True, blank=True, related_name="messages")   #is this message related to a particular case?
#    creator = models.ForeignKey(User, related_name='reminder_creator')
#    recipient = models.ForeignKey(User, related_name='reminder_recipient')
#    fire_date = models.DateField()
#    fire_time = models.TimeField(blank=True, null=True)

class Follow(models.Model):
    """
    Simple model for a user to follow a particular case
    """
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    case = models.ForeignKey(Case, null=True, blank=True, related_name="messages")   #is this message related to a particular case?
    is_public = models.BooleanField(default=False)    
    author = models.ForeignKey(User, related_name='messages_authored')    
    
#We recognize this is a nasty practice to do an import, but we hate putting signal code
#at the bottom of models.py even more.
import signals