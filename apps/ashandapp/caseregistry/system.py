from casetracker import constants
from casetracker.caseregistry import registry
from casetracker.caseregistry import CategoryBridge, StatusBridge, ActivityBridge
from casetracker.models import Category, EventActivity, Status


CATEGORY_MODULE = 'ashandapp.caseregistry.system'
SLUG_PREFIX = 'system-'

CATEGORY_SLUG = 'system'
CATGEGORY_DISPLAY = 'System'
CATEGORY_PLURAL = 'system messages'

class SystemCategory(CategoryBridge):    
    slug = CATEGORY_SLUG
    display = CATGEGORY_DISPLAY    
    plural = CATEGORY_PLURAL
    
    bridge_module = CATEGORY_MODULE
    bridge_class = 'SystemCategory'
        
    custom_create = False
    custom_read = False        

category_type_class = SystemCategory

##################################################################
#Event Activity Instances

class SystemEventOpen(ActivityBridge):
    slug = SLUG_PREFIX + 'event-open'
    summary = 'open system event'
    past_tense = 'opened'
    active_tense = 'open'
    event_class = constants.CASE_EVENT_OPEN
    custom_view = False
    category_bridge = category_type_class
    bridge_module = CATEGORY_MODULE
    bridge_class = 'SystemEventOpen'

class SystemEventView(ActivityBridge):
    slug = SLUG_PREFIX + 'event-view'
    summary = 'view system event'
    past_tense = 'viewed'
    active_tense = 'view'
    event_class = constants.CASE_EVENT_VIEW         
    custom_view = False
    category_bridge = category_type_class
    bridge_module = CATEGORY_MODULE
    bridge_class = 'SystemEventView'
    
#class IssueEventEdit(ActivityBridge):
#    slug = SLUG_PREFIX + 'event-edit'
#    summary = 'edit system event'
#    past_tense = 'edited'
#    active_tense = 'edit'
#    event_class = constants.CASE_EVENT_EDIT         
#    custom_view = False
#    category_bridge = category_type_class
#    bridge_module = CATEGORY_MODULE
#    bridge_class = 'SystemEventEdit'
#    
#class SystemEventAssign(ActivityBridge):
#    slug = SLUG_PREFIX + 'event-assign'
#    summary = 'assign system event'
#    past_tense = 'assigned'
#    active_tense = 'assign'
#    event_class = constants.CASE_EVENT_ASSIGN         
#    custom_view = False
#    category_bridge = category_type_class
#    bridge_module = CATEGORY_MODULE
#    bridge_class = 'SystemEventAssign'
#    
#class SystemEventComment(ActivityBridge):
#    slug = SLUG_PREFIX + 'event-comment'
#    summary = 'comment system event'
#    past_tense = 'commented'
#    active_tense = 'comment'
#    event_class = constants.CASE_EVENT_COMMENT         
#    custom_view = False
#    category_bridge = category_type_class
#    bridge_module = CATEGORY_MODULE
#    bridge_class = 'SystemEventComment'

#class SystemEventResolve(ActivityBridge):
#    slug = SLUG_PREFIX + 'event-resolve'
#    summary = 'resolve system event'
#    past_tense = 'resolved'
#    active_tense = 'resolve'
#    event_class = constants.CASE_EVENT_RESOLVE         
#    custom_view = False
#    category_bridge = category_type_class
#    bridge_module = CATEGORY_MODULE
#    bridge_class = 'SystemEventResolve'

class SystemEventClose(ActivityBridge):
    slug = SLUG_PREFIX + 'event-close'
    summary = 'close system event'
    past_tense = 'closed'
    active_tense = 'close'
    event_class = constants.CASE_EVENT_CLOSE         
    custom_view = False
    category_bridge = category_type_class
    bridge_module = CATEGORY_MODULE
    bridge_class = 'SystemEventClose'

#End Event Activity Instances
##################################################################


##################################################################
#Begin Status Instances



#class SystemNew(StatusBridge):
#    slug = SLUG_PREFIX + 'new-default'
#    display = 'New'
#    state_class = constants.CASE_STATE_NEW
#    category_bridge = SystemCategory
        
class SystemStateOpen(StatusBridge):
    slug = SLUG_PREFIX + 'open-default'
    display = 'Open'
    state_class = constants.CASE_STATE_OPEN
    category_bridge = SystemCategory

#class SystemResolved(StatusBridge):
#    slug = SLUG_PREFIX + 'resolved-default'
#    display = 'Resolved (default)'
#    state_class = constants.CASE_STATE_RESOLVED
#    category_bridge = SystemCategory

#class SystemResolvedCanceled(StatusBridge):
#    slug = SLUG_PREFIX + 'resolved-canceled'
#    display = 'Resolved (canceled)'
#    state_class = constants.CASE_STATE_RESOLVED
#    category_bridge = SystemCategory

class SystemStateClosed(StatusBridge):
    slug = SLUG_PREFIX + 'closed-default'
    display = 'Closed'
    state_class = constants.CASE_STATE_CLOSED
    category_bridge = SystemCategory


#End Status Instances
##################################################################


def register_category():
    registry.RegisterCategory(SystemCategory)
    
    
#    registry.RegisterStatus(SystemNew)
#    registry.RegisterActivity(SystemNew, SystemEventComment)
#    registry.RegisterActivity(SystemNew, SystemEventAssign)
#    
    registry.RegisterStatus(SystemStateOpen)
#    registry.RegisterActivity(SystemStateOpen, SystemEventComment)
#    registry.RegisterActivity(SystemStateOpen, SystemEventAssign)
#    registry.RegisterActivity(SystemStateOpen, SystemEventResolve)
    registry.RegisterActivity(SystemStateOpen, SystemEventOpen)
    registry.RegisterActivity(SystemStateOpen, SystemEventClose)
    
#    registry.RegisterStatus(SystemResolved)
#    registry.RegisterActivity(SystemResolved, SystemEventComment)
#    registry.RegisterActivity(SystemResolved, SystemEventClose)
#    
#    registry.RegisterStatus(SystemResolvedCanceled)
#    registry.RegisterActivity(SystemResolvedCanceled, SystemEventComment)
#    registry.RegisterActivity(SystemResolvedCanceled, SystemEventClose)
#    
    registry.RegisterStatus(SystemStateClosed)
#    registry.RegisterActivity(SystemStateClosed, SystemEventComment)
