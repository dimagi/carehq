from casetracker import constants
from casetracker.models import Category, Status, EventActivity
from casetracker.forms import CaseModelForm, CaseResolveCloseForm, CaseCommentForm
from django.contrib.auth.models import User


class CategoryBridge(object):
    """
    A CategoryBridge is a base class that allows a case of an arbitrary category
    to be dispatched to special view/template functions.
    
    The Category Bridge basically allows for customization of view level CRUD functionality for a case
    """
    slug = None
    display = None
    plural = None
    
    bridge_module = None
    bridge_class = None
        
    custom_create = False
    custom_read = False
            
    def __init__(self, *args, **kwargs):
        if self.slug == None:
            raise Exception("Error, you must specify a slug to match the entry to appear in the Category model table")
        if self.display == None:
            raise Exception("Error, you must specify a display string to match the entry to appear in the Category model table")
        if self.plural == None:
            raise Exception("Error, you must specify a plural string to match the entry to appear in the Category model table")
        
        if self.bridge_class == None:
            raise Exception("Error, you must specify a class to match the entry to appear in the Category model table")
        if self.bridge_module == None:
            raise Exception("Error, you must specify a module to match the entry to appear in the Category model table")
        
        
    def create_template(self, request, context, *args, **kwargs):
        """
        The create template is the template path you will use when calling the view function
        to create a new case.  This includes rendering the Form class and the actual layout of the fields on the browser.
        """
        return 'casetracker/manage/edit_case.html'
    def create_context(self, request, context, *args, **kwargs):
        """
        The create_context is a function to populate any additional context variables for your create view
        """        
        return context    
    def create_viewfunc(self, request, context, *args, **kwargs):
        """
        An optional override to completely override the default castracker.view create view function.
        """
        if not self.custom_create:
            raise Exception("Error, this bridge class is not configured to use a custom view class")
        return None
    
    def read_template(self, request, context, *args, **kwargs):
        return 'casetracker/view_case.html'    
    def read_context(self, case, request, context, *args, **kwargs):
        context['case'] = case
        return context
    def read_viewfunc(self, case, request, context, *args, **kwargs):
        """
        If a wholesale view override is desired, just implement it here.
        """
        if not self.custom_read:
            raise Exception("Error, this category bridge class is not configured to use a custom view class")            
        return None
    def get_user_list_choices(self, case):
        return User.objects.all()

class StatusBridge(object):
    slug = None    
    display = None
    state_class = None
    category_bridge = None
    def __init__(self, *args, **kwargs): 
        if self.slug == None:
            raise Exception("Error, you must specify a slug to match the entry to appear in the Status model table")
        if self.display == None:
            raise Exception("Error, you must specify a display string to match the entry to appear in the Status model table")
        if self.state_class == None:
            raise Exception("Error, you must specify the state_class string to match the entry to appear in the Status model table")
        if self.category_bridge == None:
            raise Exception("Error, you must specify the class of the category to bind this status to")

            
        

class ActivityBridge(object):
    """
    ActivityBridge is a base class that allows a case of an arbitrary category
    to be dispatched to special view/template functions.
    
    The Category Bridge basically allows for customization of view level CRUD functionlaity for a case
    """    
    slug = None
    summary = None
    past_tense = None
    
    active_tense = None
    event_class = None
            
    custom_view = False      
    
    category_bridge = None
    bridge_module = None
    bridge_class = None
    
    def __init__(self, *args, **kwargs):                       
        if self.slug == None:
            raise Exception("Error, you must specify a slug to match the entry to appear in the Activity model table")
        if self.summary == None:
            raise Exception("Error, you must specify a summary string to match the entry to appear in the Activity model table")
        if self.past_tense == None:
            raise Exception("Error, you must specify the past_tense string to match the entry to appear in the Activity model table")
        
        if self.active_tense == None:
            raise Exception("Error, you must specify the active_tense string to match the entry to appear in the Activity model table")
        
        if self.event_class == None:
            raise Exception("Error, you must specify an event_class to match the entry to appear in the Activity model table")        
        
        if self.category_bridge == None:
            raise Exception("Error, you must specify a category_bridge instance for this event activity bridge to exist")
        
        if self.bridge_class == None:
            raise Exception("Error, you must specify a bridge class to match the entry to appear in the Activity model table")
        if self.bridge_module == None:
            raise Exception("Error, you must specify a bridge module namespace to match the entry to appear in the Activity model table")

    def template(self):
        return 'casetracker/manage/view_case.html'
    
    def form_class(self):
        if self.event_class == constants.CASE_EVENT_RESOLVE or self.event_class==constants.CASE_EVENT_CLOSE:
            return CaseResolveCloseForm
        elif self.event_class == constants.CASE_EVENT_COMMENT:
            return CaseCommentForm
        else:
            return CaseModelForm
            
    
    def context_handler(self, case, request, context, *args, **kwargs):
        context['case'] = case
        return context
        
    def custom_view_func(self, case, request, context, *args, **kwargs):
        if not self.custom_view:
            raise Exception("Error, this Activity bridge class is not configured to use a custom view class")
        return None
    
    @staticmethod
    def make_new_default(category):
        newslug = category.slug + "-edit-default"
        past_tense = "edited"
        active_tense = "edit"        
        return ActivityBridge(category, newslug, past_tense, active_tense, constants.CASE_EVENT_EDIT,'default case edit', custom_view=False)

