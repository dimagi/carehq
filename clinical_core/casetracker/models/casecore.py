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
        app_label = 'casetracker'
        verbose_name = "Priority Type"
        verbose_name_plural = "Priority Types"
        ordering = ['magnitude']


class Category(models.Model):
    """
    The Category is the central piece of the casetracker model tree.
    
    All cases must embody a certain category.
    
    A category then is the handler between the existence of a case in the database and how it is handled between the database
    and other types within pythonland.
    
    So, in ashand, you define different cases as different classes of "case-able" information.
    So, a case can be an issue, question, or alerts from some therapeutic monitor or scheduling - the list goes on.
    
    To keep the purity of the casetracker app, other models that wish to add itself to the casetracker.
    """
    id = models.CharField(_('Unique id'), max_length=32, unique=True, default=make_uuid, primary_key=True) #primary_key override?
    slug = models.SlugField(unique=True, help_text = "The unique, internal represntation of the category, for the in memory registry") #Unique slug name of category for the in memory registry
    display = models.CharField(max_length=64, help_text="The display name of the category - what will be printed")
    description = models.CharField(max_length=255, help_text = "A longer description of the case category")

    @property
    def read_template(self):
        #get the template from the CategoryHandler registry
        pass

    @property
    def read_context(self):
        #get the context from the CategoryHandler registry
        pass

    @property
    def handler(self): #from handler
        """
        Returns the class instance of the category category
        """
        #pull from the in memory cache
        pass

    
    def __unicode__(self):
        return "%s" % (self.slug)
    class Meta:
        app_label = 'casetracker'
        verbose_name = "Category Type"
        verbose_name_plural = "Category Types"
        ordering = ['display']

class Status (models.Model):
    """
    Status is the model to capture the different states of a case.
    In Fogbugz, these are also classified within the category of the original bug.
    ie, a bug's status states will be fundamentally different from a Feature or Question.
    """    
    id = models.CharField(_('Unique id'), max_length=32, unique=True, default=make_uuid, primary_key=True) #primary_key override?
    slug = models.SlugField(unique=True)
    display = models.CharField(max_length=64) #from description
    state_class = models.TextField(max_length=24, choices=CASE_STATES)
    
    #query filters can be implemented a la kwarg evaluation:
    #http://stackoverflow.com/questions/310732/in-django-how-does-one-filter-a-queryset-with-dynamic-field-lookups/659419#659419        
    #Note: 
    #fogbugz had a bunch of classifiers here that describe the nature of the status
    #in other words they should still fall within the 4 main  classifiers of status:
    #resolved, duplicate, deleted, done?
    def __unicode__(self):
        return "Status: %s" % (self.display)

    class Meta:
        app_label = 'casetracker'
        verbose_name = "Case Status Type"
        verbose_name_plural = "Case Status Types"
        ordering = ['display']
    


class ActivityClass(models.Model):
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
    id = models.CharField(_('Unique id'), max_length=32, unique=True, default=make_uuid, primary_key=True) #primary_key override?
    slug = models.SlugField(unique=True) #from name
    past_tense = models.CharField(max_length=64, help_text = "The past tense description of this activity") #from phrasing
    active_tense = models.CharField(max_length=64, help_text = "The active tense of this activity - this text will be displayed as a button in the case view.") #present as button on case view
    event_class = models.TextField(max_length=32, choices=CASE_EVENT_CHOICES, help_text = "The primitive class of this event.") # what class of event is it?
    summary = models.CharField(max_length=255)

    ######################
    #target_status is currently unused (3/17/2010), however there may come a time for events to be totally manage
    #via the DB, so this field is being kept live in the model even though it has no use at the moment.
    target_status = models.ForeignKey("Status", blank=True, null=True,
                                      help_text=_("This event activity may alter the case's status.  If it does, it must exist here.",
                                    related_name="set_by_activities"))

    
    def __unicode__(self):
        return "[%s] Activity" % (self.slug)

    class Meta:
        app_label = 'casetracker'
        verbose_name = "Case Event Activity Type"
        verbose_name_plural = "Case Event Activity Types"        
        ordering=['event_class', 'slug']


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
    
    activity = models.ForeignKey(ActivityClass)
    
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
        return "Event (%s} by %s on %s" % (self.activity.slug, self.created_by.title(), self.created_date.strftime("%I:%M%p %Z %m/%d/%Y"))
    
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
    orig_description = models.CharField(max_length=160, blank=True, null=True, editable=False)    

    category = models.ForeignKey(Category, verbose_name=_('Category'))
    status = models.ForeignKey(Status, verbose_name=_('Status'))    
    
    patient = models.ForeignKey(Patient, blank=True, null=True)

    body = models.TextField(blank=True, null=True)    
    
    priority = models.ForeignKey(Priority)    
    
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
        state_class = self.status.state_class
        if state_class == constants.CASE_STATE_RESOLVED: #from choices of CASE_STATES
            if self.resolved_by == None:
                raise Exception("Case state is now resolved, you must set a resolved_by")
            else:
                self.resolved_date = datetime.utcnow()
        elif state_class == constants.CASE_STATE_CLOSED:
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
    
#
#class Follow(models.Model):
#    """
#    Simple model for a user to follow a particular case
#    """
#    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
#    case = models.ForeignKey(Case, null=True, blank=True, related_name="messages")   #is this message related to a particular case?
#    is_public = models.BooleanField(default=False)
#    author = models.ForeignKey(Actor, related_name='messages_authored')
    

    
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
        (-ONE_DAY, 'In the past day'),
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
    id = models.CharField(_('Unique id'), max_length=32, unique=True, default=make_uuid, primary_key=True) #primary_key override?
    
    #metadata about the query
    description = models.CharField(max_length=64)
    creator = models.ForeignKey(Actor, related_name="filter_creator")
    shared = models.BooleanField(default=False)
    
    
    custom_function=models.BooleanField(default=False)
    #Code based filter functions    
    filter_module = models.CharField(max_length=128, blank=True, null=True,
                                      help_text=_("This is the fully qualified name of the module that implements the filter function."))
    
    filter_class = models.CharField(max_length=64, blank=True, null=True,
                                     help_text=_('This is the actual method name of the model filter you wish to run.'))
    
    #case related properties
    category = models.ForeignKey(Category, null=True, blank=True)
    status = models.ForeignKey(Status, null=True, blank=True)
    priority = models.ForeignKey(Priority, null=True, blank=True)
    
    opened_by = models.ForeignKey(Actor, null=True, blank=True, related_name="filter_opened_by")
    assigned_to = models.ForeignKey(Actor, null=True, blank=True, related_name="filter_assigned_to")
    last_edit_by = models.ForeignKey(Actor, null=True, blank=True, related_name="filter_last_edit_by")    
    resolved_by = models.ForeignKey(Actor, null=True, blank=True, related_name="filter_resolved_by")
    closed_by = models.ForeignKey(Actor, null=True, blank=True, related_name="filter_closed_by")
        
    opened_date = models.IntegerField(choices=TIME_DURATION_PAST_CHOICES, null=True, blank=True)
    assigned_date = models.IntegerField(choices=TIME_DURATION_PAST_CHOICES, null=True, blank=True)    
    last_edit_date = models.IntegerField(choices=TIME_DURATION_PAST_CHOICES, null=True, blank=True)
    resolved_date = models.IntegerField(choices=TIME_DURATION_PAST_CHOICES, null=True, blank=True)
    closed_date = models.IntegerField(choices=TIME_DURATION_PAST_CHOICES, null=True, blank=True)
    
    #case Event information
    last_event_type = models.ForeignKey(ActivityClass, null=True, blank=True)
    last_event_date = models.IntegerField(choices=TIME_DURATION_PAST_CHOICES, null=True, blank=True)
    last_event_by = models.ForeignKey(Actor, null=True, blank=True)
    

    def get_absolute_url(self):        
        return '/filter/%s' % self.id

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
        if self.assigned_date:
            compare_date = utcnow + timedelta(days=self.assigned_date)
            case_query_arr.append(Q(assigned_date__gte=compare_date))
        if self.last_edit_date:
            compare_date = utcnow + timedelta(days=self.last_edit_date)
            case_query_arr.append(Q(last_edit_date__gte=compare_date))
        if self.resolved_date:
            compare_date = utcnow + timedelta(days=self.resolved_date)
            case_query_arr.append(Q(resolved_date__gte=compare_date))
        if self.closed_date:
            compare_date = utcnow + timedelta(days=self.closed_date)
            case_query_arr.append(Q(closed_date__gte=compare_date))
        
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
            #print "case event subquery"
            case_events = CaseEvent.objects.select_related().all()                  
            for qe in case_event_query_arr:
                case_events = case_events.filter(qe)
            
            #get all the case ids from the case event filters
            case_events_cases_ids = case_events.values_list('case', flat=True)        
            
            if len(case_events_cases_ids) > 0:
                cases = cases.filter(pk__in=case_events_cases_ids)
                            
        return cases
        
    def __unicode__(self):
        return "Model Filter - %s" % (self.description)
    
    class Meta:
        app_label = 'casetracker'
        verbose_name = "Model Filter"
        verbose_name_plural = "Model Filters"
        
    @property
    def get_gridpreference(self):
        if not hasattr(self, '_gridpreference'):
            self._gridpreference = self.gridpreference
        return self._gridpreference