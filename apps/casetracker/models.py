from django.db import models

from django.db.models import Q
from django.contrib.auth.models import User

from datetime import datetime, timedelta


class CaseAction(models.Model):
    """
    A case action is a descriptor for capturing the types of actions you can actuate upon a case.
    These are linked to a case to describe the desired NEXT action to take upon a case.
    
    In this case, we want to be able to capture the differing types of 'todo for next time' actions you 
    can assign to a case.
    
    The main desired actions are
    Follow up w/ subject: A date bound action that says I should follow up with the patient
    To Resolve: A date bound action that says I should finish said case by the next_action_date - which effectively becomes a due date.
    """
    description = models.CharField(max_length=64)
    #date_bound = models.BooleanField() # does this seem necessary - all cases seem date bound
    
    def __unicode__(self):
        return "%d - %s" % (self.id, self.description)
    
    class Meta:
        verbose_name = "Case Action Type"
        verbose_name_plural = "Case Action Types"

    
class Category(models.Model):
    """A category tries to capture the original nature of the opened case
    
    In Ashand, this is akin to the divisions within issue/case/risk.
    
    Simple setups will be:
    Inquiry
    Issue    
    
    Schedule Item    
        Appointment
        Order
        Prescription    
    """
    category = models.CharField(max_length=32)
    plural = models.CharField(max_length=32)    
    default_status = models.ForeignKey("Status", blank=True, null=True, related_name="Default Status") #this circular is nullable in FB
    def __unicode__(self):
        return "%s" % (self.category)
    class Meta:
        verbose_name = "Category Type"
        verbose_name_plural = "Category Types"

    
class Priority(models.Model):
    """
    Priorities are assigned on a case basis, and are universally assigned.
    Sorting would presumably need to be defined first by case category, then by priority    
    """    
    description = models.CharField(max_length=32)
    default = models.BooleanField()    
    def __unicode__(self):
        return "%d - %s" % (self.id, self.description)

    class Meta:
        verbose_name = "Priority Type"
        verbose_name_plural = "Priority Types"


class Status (models.Model):
    """
    Status is the model to capture the different states of a case.
    In Fogbugz, these are also classified within the category of the original bug.
    ie, a bug's status states will be fundamentally different from a Feature or Inquiry.
    """
    
    description = models.CharField(max_length=64)
    category = models.ForeignKey(Category)
    
    #query filters can be implemented a la kwarg evaluation:
    #http://stackoverflow.com/questions/310732/in-django-how-does-one-filter-a-queryset-with-dynamic-field-lookups/659419#659419
        
    #Note: 
    #fogbugz had a bunch of classifiers here that describe the nature of the status
    #in other words they should still fall within the 4 main  classifiers of status:
    #resolved, duplicate, deleted, done?
    def __unicode__(self):
        return "[%s - Status] %s" % (self.category, self.description)

    class Meta:
        verbose_name = "Case Status Type"
        verbose_name_plural = "Case Status Types"
        ordering = ['category','id']
    


class EventActivity(models.Model):
    """
    An Event Activity describes sanction-able actions that can be done revolving around a case.
    The hope for this as these are models, are that distinct functional actions can be modeled around these
    Event Activities.
    
    For example:
    edit case
    
    email
    make a phone call
    sms    
        
    """
    EVENT_CLASS_CHOICES = (
        ('open', 'Open/Create'),
        ('view', 'View'),
        ('edit', 'Edit'),        
        ('resolve', 'Resolve'),
        ('close', 'Close'),        
        ('reopen', 'Reopen'),
        
        ('custom', 'Custom'),   #custom are activites that don't resolve around the basic open/edit/view/resolve/close
    )
    
    name = models.TextField(max_length=64)
    summary = models.TextField(max_length=512)
    category = models.ForeignKey(Category) # different categories have different event types
    
    event_class = models.TextField(max_length=24, choices=EVENT_CLASS_CHOICES)
    #activity_method = models.CharField(max_length=512, null=True) # this can be some sort of func call?
    def __unicode__(self):
        return "(%s) [%s] Activity" % (self.category, self.name)

    class Meta:
        verbose_name = "Case Event Activity Type"
        verbose_name_plural = "Case Event Activity Types"


class CaseEvent(models.Model):
    """
    A CaseEvent is any action done revolving around a case.
    A Interaction in our book is an actual medical document that happens for a particular medical document/domain.
    
    An encounter in this scope is an action that happens and is resolved around a particular case.
    
    It is meant to capture outside the scope of the case table itself, the actions and their accompanying
    examples of what happened to a case.
    """
    
    case = models.ForeignKey("Case")    
    notes = models.TextField(blank=True)
    #activity = models.ForeignKey(EventActivity, limit_choices_to = {'category': "case__category"})    
    activity = models.ForeignKey(EventActivity)
    
    created_date  = models.DateTimeField()
    created_by = models.ForeignKey(User)
    
    
    def save(self):   
        if self.id == None:     
            if self.created_by == None:
                raise Exception("Missing fields in Case creation - created by")           
                self.created_date = datetime.utcnow()                            
        super(CaseEvent, self).save()  
    
    def __unicode__(self):
        return "Case Event: %s - %s" % (self.created_by.username, self.created_date)
    
    class Meta:
        verbose_name = "Case Event"
        verbose_name_plural = "Case Events"
        ordering = ['-created_date']

    

class Case(models.Model):
    """
    A case in this system is the actual even that needs due diligence and subsequent closure.
    
    These are finite and discrete tasks that must be done.  Linking these cases to someone or something
    must be implemented elsewhere. 
    
    The scope of these cases are currently attached to the actual agents that need to work on them.
    
    Changes to these cases will be managed by django-reversion.  Actions revolving around these cases will be done via encounters.
    """    
    description = models.CharField(max_length=160)
    orig_description = models.CharField(max_length=160, blank=True, null=True, editable=False)    
    category = models.ForeignKey(Category)
    status = models.ForeignKey(Status)    
    
    priority = models.ForeignKey(Priority)
    
    next_action = models.ForeignKey(CaseAction, null=True)
    
    opened_date  = models.DateTimeField()
    opened_by = models.ForeignKey(User, related_name="Opened by")
    
    last_edit_date = models.DateTimeField(null=True, blank=True)
    last_edit_by = models.ForeignKey(User, related_name="Last edit by", null=True, blank=True) 
        
    next_action_date = models.DateTimeField(null=True, blank=True)
    
    resolved_date  = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, related_name="Resolved by", null=True, blank=True)
        
    closed_date  = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(User, related_name="Closed by", null=True, blank=True)    
    
    assigned_to = models.ForeignKey(User, related_name="Assigned to", null=True, blank=True)   
    
    parent_case = models.ForeignKey('self', null=True, blank=True)
    
    
    @property
    def last_case_event(self):
        if CaseEvent.objects.filter(case=self).order_by('-created_date').count() > 0:
            return CaseEvent.objects.filter(case=self).order_by('-created_date')[0]
        else:
            return None
        
        
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
    
    
    
    
    def save(self):        
        if self.id == None:
            if self.opened_by == None or self.description == None:
                raise Exception("Missing fields in Case creation - opened by and description")            
            
            #if we're brand new, we'll update the dates in this way:
            self.opened_date = datetime.utcnow()
            self.orig_description = self.description
        else:
            if self.last_edit_by == None:
                raise Exception("Missing fields in Case edit - last_edit_by")            

            self.last_edit_date = datetime.utcnow()            
                    
        super(Case, self).save()        
    
    def __unicode__(self):
        return "(Case %s) %s" % (self.id, self.description)
    class Meta:
        verbose_name = "Case"
        verbose_name_plural="Cases"
        ordering = ['-opened_date']


class Filter(models.Model):
    """
    
    """

    #below are the enumerated integer choices because integer fields don't like choices that aren't ints.
    #for more information see here:
    #http://www.b-list.org/weblog/2007/nov/02/handle-choices-right-way/
    TODAY=0
    ONE_DAY=1
    THREE_DAYS=3
    ONE_WEEK=7
    TWO_WEEKS=14
    ONE_MONTH=30
    TWO_MONTHS=60
    THREE_MONTHS=90
    SIX_MONTHS=180
    ONE_YEAR=365
    
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
    shared = models.BooleanField(default = False)
    
    #case related properties
    category = models.ForeignKey(Category, null=True, blank=True)
    status = models.ForeignKey(Status, null=True, blank=True)
    priority = models.ForeignKey(Priority, null=True, blank=True)
    
    assigned_to = models.ForeignKey(User, null=True, blank=True, related_name="assigned_to")
    opened_by = models.ForeignKey(User, null=True, blank=True, related_name="opened_by")
    last_edit_by = models.ForeignKey(User, null=True, blank=True, related_name="last_edit_by")    
    resolved_by = models.ForeignKey(User, null=True, blank=True, related_name="resolved_by")
    closed_by = models.ForeignKey(User, null=True, blank=True, related_name="closed_by")
        
    opened_date = models.IntegerField(choices = TIME_DURATION_PAST_CHOICES, null=True, blank=True)
    last_edit_date = models.IntegerField(choices = TIME_DURATION_PAST_CHOICES, null=True, blank=True)
    resolved_date = models.IntegerField(choices = TIME_DURATION_PAST_CHOICES, null=True, blank=True)
    closed_date = models.IntegerField(choices = TIME_DURATION_PAST_CHOICES, null=True, blank=True)
    
    next_action_date = models.IntegerField(choices = TIME_DURATION_FUTURE_CHOICES, null=True, blank=True)    
    
    #case Event information
    last_event_type = models.ForeignKey(EventActivity, null=True, blank=True)
    last_event_date = models.IntegerField(choices = TIME_DURATION_PAST_CHOICES, null=True, blank=True)
    last_event_by = models.ForeignKey(User, null=True, blank=True)
    
    
    #this should come in as a dictionary of key-value pairs that are compatible with a 
    #django query when resolved as a kwargs.
    #http://stackoverflow.com/questions/310732/in-django-how-does-one-filter-a-queryset-with-dynamic-field-lookups
    #http://stackoverflow.com/questions/353489/cleaner-way-to-query-on-a-dynamic-number-of-columns-in-django
       
    
    def get_filter_queryset(self):
        """
        On a given filter instance, we will generate a query 
        """        
        utcnow = datetime.utcnow()
                
        case_query_arr = []        
        case_event_query_arr = []
        
        if self.category:
            case_query_arr.append(Q(category=self.category))        
        if self.status:
            case_query_arr.append(Q(status = self.status))
        if self.priority:
            case_query_arr.append(Q(priority = self.priority))
        if self.assigned_to:
            case_query_arr.append(Q(assigned_to = self.assigned_to))        
        if self.opened_by:
            case_query_arr.append(Q(opened_by = self.opened_by))
        if self.last_edit_by:
            case_query_arr.append(Q(last_edit_by = self.last_edit_by))
        if self.resolved_by:
            case_query_arr.append(Q(resolved_by = self.resolved_by))
        if self.closed_by:
            case_query_arr.append(Q(closed_by = self.closed_by))
        
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
            case_event_query_arr.append(Q(activity=self.last_event_by))
            
        if self.last_event_date:        
            compare_date = utcnow + timedelta(days=self.last_event_date)
            case_event_query_arr.append(Q(created_date__gte=self.last_event_date))            

        #now, we got the queries built up, let's run the queries                
        cases = Case.objects.all()        
        for qu in case_query_arr:
            #dmyung 12-8-2009
            #doing the filters iteratively doesn't seem to be the best way.  there ought to be a way to chain
            #them all in an evaluation to the filter() call a-la the kwargs or something.  since these
            # are ANDED, we want them to be done sequentially (ie, filter(q1,q2,q3...)
            #negations should be handled by the custom search            
            cases = cases.filter(qu)
        
        if len(case_event_query_arr) > 0:            
            case_events = CaseEvent.objects.all()
            print len(case_events)        
            for qe in case_event_query_arr:
                case_events = case_events.filter(qe)
            
            #get all the case ids from the case event filters
            case_events_cases_ids = case_events.values_list('case',flat=True)        
            
            if len(case_events_cases_ids) > 0:
                cases = cases.filter(pk__in=case_events_cases_ids)
        return cases
        
    def __unicode__(self):
        return "Filter - %s" % (self.description)

    class Meta:
        verbose_name = "Case Filter"
        verbose_name_plural = "Case Filters"


class GridColumn(models.Model):
    name = models.CharField(max_length=32)
    def __unicode__(self):
        return self.name


class GridSort(models.Model):
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

class GridOrder (models.Model):
    column = models.ForeignKey("GridColumn", related_name='gridcolumn_displayorder')
    preference = models.ForeignKey("GridPreference", related_name="gridpreference_displayorder")
    order = models.PositiveIntegerField()

class GridPreference(models.Model):
    filter = models.OneToOneField(Filter)
    display_columns = models.ManyToManyField(GridColumn, through=GridOrder, related_name="display_columns")
    sort_columns = models.ManyToManyField(GridColumn, through=GridSort, related_name = "sort_columns")
    
    def __unicode__(self):
        return "Grid Display Preference: %s" % self.filter.description
    
    


#We recognize this is a nasty practice to do an import, but we hate putting signal code
#at the bottom of models.py even more.
import signals