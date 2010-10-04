from casetracker import constants
from casetracker.registry import registry
from casetracker.registry import CategoryHandler, StatusBridge, ActivityBridge
from casetracker.models import Category, ActivityClass, Status

from ashandapp.caseregistry import ashand_case_context, get_careteam_assignment_choices


CATEGORY_MODULE = 'ashandapp.caseregistry.question'
SLUG_PREFIX = 'question-'

CATEGORY_SLUG = 'ashand-question'
CATEGORY_DISPLAY = 'Question'
CATEGORY_PLURAL = 'questions'

class QuestionCategory(CategoryHandler):
    slug = CATEGORY_SLUG
    display = CATEGORY_DISPLAY    
    plural = CATEGORY_PLURAL
    
    bridge_module = CATEGORY_MODULE
    bridge_class = 'QuestionCategory'
        
    custom_create = False
    custom_read = False        
    def read_template(self, request, context, *args, **kwargs):
        return 'ashandapp/cases/view_question.html'    
    
    def read_context(self, case, request, context, *args, **kwargs):        
        return ashand_case_context(case, request, context)        
        
    def get_user_list_choices(self, case):
        return get_careteam_assignment_choices(case)

category_type_class = QuestionCategory

##################################################################
#Event Activity Instances

QuestionEventOpen = ActivityBridge(\
    slug = SLUG_PREFIX + 'event-open',
    summary = 'open question',
    past_tense = 'opened',
    active_tense = 'open',
    event_class = constants.CASE_EVENT_OPEN,         
    custom_view = False,
    category_bridge = category_type_class,
    bridge_module = CATEGORY_MODULE,
    bridge_class = 'QuestionEventOpen')

QuestionEventView = ActivityBridge(\
    slug = SLUG_PREFIX + 'event-view',
    summary = 'view question',
    past_tense = 'viewed',
    active_tense = 'view',
    event_class = constants.CASE_EVENT_VIEW,         
    custom_view = False,
    category_bridge = category_type_class,
    bridge_module = CATEGORY_MODULE,
    bridge_class = 'QuestionEventView')
    
QuestionEventEdit = ActivityBridge(\
    slug = SLUG_PREFIX + 'event-edit',
    summary = 'edit question',
    past_tense = 'edited',
    active_tense = 'edit',
    event_class = constants.CASE_EVENT_EDIT,         
    custom_view = False,
    category_bridge = category_type_class,
    bridge_module = CATEGORY_MODULE,
    bridge_class = 'QuestionEventEdit')
    
QuestionEventAssign = ActivityBridge(\
    slug = SLUG_PREFIX + 'event-assign',
    summary = 'assign question',
    past_tense = 'assigned',
    active_tense = 'assign',
    event_class = constants.CASE_EVENT_ASSIGN,         
    custom_view = False,
    category_bridge = category_type_class,
    bridge_module = CATEGORY_MODULE,
    bridge_class = 'QuestionEventAssign')
    
QuestionEventComment = ActivityBridge(\
    slug = SLUG_PREFIX + 'event-comment',
    summary = 'comment issue',
    past_tense = 'commented',
    active_tense = 'comment',
    event_class = constants.CASE_EVENT_COMMENT,         
    custom_view = False,
    category_bridge = category_type_class,
    bridge_module = CATEGORY_MODULE,
    bridge_class = 'QuestionEventComment')

QuestionEventResolve = ActivityBridge(\
    slug = SLUG_PREFIX + 'event-resolve',
    summary = 'answer question',
    past_tense = 'answered',
    active_tense = 'answer',
    event_class = constants.CASE_EVENT_RESOLVE,         
    custom_view = False,
    category_bridge = category_type_class,
    bridge_module = CATEGORY_MODULE,
    bridge_class = 'QuestionEventResolve')

QuestionEventClose = ActivityBridge(\
    slug = SLUG_PREFIX + 'event-close',
    summary = 'close question',
    past_tense = 'closed',
    active_tense = 'close',
    event_class = constants.CASE_EVENT_CLOSE,         
    custom_view = False,
    category_bridge = category_type_class,
    bridge_module = CATEGORY_MODULE,
    bridge_class = 'QuestionEventClose')

#End Event Activity Instances
##################################################################


##################################################################
#Begin Status Instances



#class QuestionNew = StatusBridge(\
#    slug = SLUG_PREFIX + 'new-default'
#    display = 'New'
#    state_class = constants.CASE_STATE_NEW
#    category_bridge = category_type_class

    
QuestionOpen = StatusBridge(\
    slug = SLUG_PREFIX + 'open-default',
    display = 'Open',
    state_class = constants.CASE_STATE_OPEN,
    category_bridge = category_type_class)

QuestionResolved = StatusBridge(\
    slug = SLUG_PREFIX + 'resolved-default',
    display = 'Resolved (default)',
    state_class = constants.CASE_STATE_RESOLVED,
    category_bridge = category_type_class)

QuestionResolvedCanceled = StatusBridge(\
    slug = SLUG_PREFIX + 'resolved-canceled',
    display = 'Resolved (canceled)',
    state_class = constants.CASE_STATE_RESOLVED,
    category_bridge = category_type_class)

QuestionClosed = StatusBridge(\
    slug = SLUG_PREFIX + 'closed-default',
    display = 'Closed',
    state_class = constants.CASE_STATE_CLOSED,
    category_bridge = category_type_class)


#End Status Instances
##################################################################


def register_category():
    registry.RegisterCategory(QuestionCategory)
    registry.RegisterStatelessActivity(QuestionEventOpen)    
    
#    registry.RegisterStatus(QuestionNew)    
#    registry.RegisterActivity(QuestionNew, QuestionEventComment)
#    registry.RegisterActivity(QuestionNew, QuestionEventAssign)
    
    registry.RegisterStatus(QuestionOpen)    
    registry.RegisterActivity(QuestionOpen, QuestionEventEdit)
    registry.RegisterActivity(QuestionOpen, QuestionEventComment)
    registry.RegisterActivity(QuestionOpen, QuestionEventAssign)
    registry.RegisterActivity(QuestionOpen, QuestionEventResolve)
    
    registry.RegisterStatus(QuestionResolved)
    registry.RegisterActivity(QuestionResolved, QuestionEventComment)
    registry.RegisterActivity(QuestionResolved, QuestionEventClose)
    
    registry.RegisterStatus(QuestionResolvedCanceled)
    registry.RegisterActivity(QuestionResolvedCanceled, QuestionEventComment)
    registry.RegisterActivity(QuestionResolvedCanceled, QuestionEventClose)
    
    registry.RegisterStatus(QuestionClosed)
    registry.RegisterActivity(QuestionClosed, QuestionEventComment)
