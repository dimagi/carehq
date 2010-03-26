from casetracker import constants
from casetracker.caseregistry import registry
from casetracker.caseregistry import CategoryBridge, StatusBridge, ActivityBridge
from casetracker.models import Category, EventActivity, Status

from ashandapp.caseregistry import ashand_case_context, get_careteam_assignment_choices

CATEGORY_MODULE = 'ashandapp.caseregistry.issue'
SLUG_PREFIX = 'issue-'

CATEGORY_SLUG = 'ashand-issue'
CATEGORY_DISPLAY = 'Issue'
CATEGORY_PLURAL = 'issues'

class IssueCategory(CategoryBridge):    
    slug = CATEGORY_SLUG
    display = CATEGORY_DISPLAY    
    plural = CATEGORY_PLURAL
    
    bridge_module = CATEGORY_MODULE
    bridge_class = 'IssueCategory'
        
    custom_create = False
    custom_read = False        
    
    def read_template(self, request, context, *args, **kwargs):
        return 'ashandapp/cases/view_question.html'    
    
    def read_context(self, case, request, context, *args, **kwargs):        
        return ashand_case_context(case, request, context)        
        
    def get_user_list_choices(self, case):
        return get_careteam_assignment_choices(case)

        

category_type_class = IssueCategory


##################################################################
#Begin Status Instances



#class IssueNew(StatusBridge):
#    slug = SLUG_PREFIX + 'new-default'
#    display = 'New'
#    state_class = constants.CASE_STATE_NEW
#    category_bridge = category_type_class

    
class IssueOpen(StatusBridge):
    slug = SLUG_PREFIX + 'open-default'
    display = 'Open'
    state_class = constants.CASE_STATE_OPEN
    category_bridge = category_type_class

class IssueResolved(StatusBridge):
    slug = SLUG_PREFIX + 'resolved-default'
    display = 'Resolved (default)'
    state_class = constants.CASE_STATE_RESOLVED
    category_bridge = category_type_class

class IssueResolvedCanceled(StatusBridge):
    slug = SLUG_PREFIX + 'resolved-canceled'
    display = 'Resolved (canceled)'
    state_class = constants.CASE_STATE_RESOLVED
    category_bridge = category_type_class

class IssueClosed(StatusBridge):
    slug = SLUG_PREFIX + 'closed-default'
    display = 'Closed'
    state_class = constants.CASE_STATE_CLOSED
    category_bridge = category_type_class


#End Status Instances
##################################################################

##################################################################
#Event Activity Instances

class IssueEventOpen(ActivityBridge):
    slug = SLUG_PREFIX + 'event-open'
    summary = 'open issue'
    past_tense = 'opened'
    active_tense = 'open'
    event_class = constants.CASE_EVENT_OPEN         
    custom_view = False
    category_bridge = category_type_class
    bridge_module = CATEGORY_MODULE
    bridge_class = 'IssueEventOpen'

class IssueEventView(ActivityBridge):
    slug = SLUG_PREFIX + 'event-view'
    summary = 'view issue'
    past_tense = 'viewed'
    active_tense = 'view'
    event_class = constants.CASE_EVENT_VIEW         
    custom_view = False
    category_bridge = category_type_class
    bridge_module = CATEGORY_MODULE
    bridge_class = 'IssueEventView'
    
class IssueEventEdit(ActivityBridge):
    slug = SLUG_PREFIX + 'event-edit'
    summary = 'edit issue'
    past_tense = 'edited'
    active_tense = 'edit'
    event_class = constants.CASE_EVENT_EDIT         
    custom_view = False
    category_bridge = category_type_class
    bridge_module = CATEGORY_MODULE
    bridge_class = 'IssueEventEdit'
    
class IssueEventAssign(ActivityBridge):
    slug = SLUG_PREFIX + 'event-assign'
    summary = 'assign issue'
    past_tense = 'assigned'
    active_tense = 'assign'
    event_class = constants.CASE_EVENT_ASSIGN         
    custom_view = False
    category_bridge = category_type_class
    bridge_module = CATEGORY_MODULE
    bridge_class = 'IssueEventAssign'
    
class IssueEventComment(ActivityBridge):
    slug = SLUG_PREFIX + 'event-comment'
    summary = 'comment issue'
    past_tense = 'commented'
    active_tense = 'comment'
    event_class = constants.CASE_EVENT_COMMENT         
    custom_view = False
    category_bridge = category_type_class
    bridge_module = CATEGORY_MODULE
    bridge_class = 'IssueEventComment'

class IssueEventResolve(ActivityBridge):
    slug = SLUG_PREFIX + 'event-resolve'
    summary = 'resolve issue'
    past_tense = 'resolved'
    active_tense = 'resolve'
    event_class = constants.CASE_EVENT_RESOLVE         
    custom_view = False    
    category_bridge = category_type_class
    bridge_module = CATEGORY_MODULE
    bridge_class = 'IssueEventResolve'
    

class IssueEventClose(ActivityBridge):
    slug = SLUG_PREFIX + 'event-close'
    summary = 'close issue'
    past_tense = 'closed'
    active_tense = 'close'
    event_class = constants.CASE_EVENT_CLOSE         
    custom_view = False
    category_bridge = category_type_class
    bridge_module = CATEGORY_MODULE
    bridge_class = 'IssueEventClose'

#End Event Activity Instances
##################################################################




def register_category():
    registry.RegisterCategory(IssueCategory)
    registry.RegisterStatelessActivity(IssueEventOpen)    
    
#    registry.RegisterStatus(IssueNew)    
#    registry.RegisterActivity(IssueNew, IssueEventComment)
#    registry.RegisterActivity(IssueNew, IssueEventAssign)
    
    registry.RegisterStatus(IssueOpen)    
    registry.RegisterActivity(IssueOpen, IssueEventEdit)
    registry.RegisterActivity(IssueOpen, IssueEventComment)
    registry.RegisterActivity(IssueOpen, IssueEventAssign)
    registry.RegisterActivity(IssueOpen, IssueEventResolve)
    
    registry.RegisterStatus(IssueResolved)
    registry.RegisterActivity(IssueResolved, IssueEventComment)
    registry.RegisterActivity(IssueResolved, IssueEventClose)
    
    registry.RegisterStatus(IssueResolvedCanceled)
    registry.RegisterActivity(IssueResolvedCanceled, IssueEventComment)
    registry.RegisterActivity(IssueResolvedCanceled, IssueEventClose)
    
    registry.RegisterStatus(IssueClosed)
    registry.RegisterActivity(IssueClosed, IssueEventComment)
