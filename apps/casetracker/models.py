from django.db import models

from django.db.models import Q
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from datetime import datetime

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
    title = models.CharField(max_length=160)
    orig_title = models.CharField(max_length=160, blank=True, null=True, editable=False)    
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
    
    
    def save(self):        
        if self.id == None:
            if self.opened_by == None or self.title == None:
                raise Exception("Missing fields in Case creation - opened by and title")            
            
            #if we're brand new, we'll update the dates in this way:
            self.opened_date = datetime.utcnow()
            self.orig_title = self.title
        else:
            if self.last_edit_by == None:
                raise Exception("Missing fields in Case edit - last_edit_by")            

            self.last_edit_date = datetime.utcnow()            
                    
        super(Case, self).save()        
    
    def __unicode__(self):
        return "(Case %s) %s" % (self.id, self.title)
    class Meta:
        verbose_name = "Case"
        verbose_name_plural="Cases"
        ordering = ['-opened_date']



#We recognize this is a nasty practice to do an import, but we hate putting signal code
#at the bottom of models.py even more.
import signals