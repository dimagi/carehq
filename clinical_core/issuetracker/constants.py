#system constants
SYSTEM_USERNAME='ASHand-System'

#constants for model Status
#CASE_STATE_NEW = 'state-new' # a state-new case is one that is brand new and unassigned, needing triageing.
CASE_STATE_OPEN = 'state-open'
CASE_STATE_RESOLVED = 'state-resolved'
CASE_STATE_CLOSED = 'state-closed'


#constants for case event activities
CASE_EVENT_OPEN = 'event-open'
CASE_EVENT_VIEW = 'event-view'
CASE_EVENT_EDIT = 'event-edit'
CASE_EVENT_ASSIGN = 'event-assign'
CASE_EVENT_WORKING = 'event-working'
CASE_EVENT_COMMENT = 'event-comment'
CASE_EVENT_CUSTOM = 'event-custom'

CASE_EVENT_REOPEN = 'event-reopen'
CASE_EVENT_RESOLVE = 'event-resolve'
CASE_EVENT_CLOSE = 'event-close'


CATEGORY_CHOICES = (
    ('threshold', 'Threshold Violation'),
    ('appointment', 'Appointment'),
    ('message', 'Message'),
)


CASE_EVENT_CHOICES = (
        (CASE_EVENT_OPEN, 'Open/Create'), #case state
        (CASE_EVENT_VIEW, 'View'),
        (CASE_EVENT_EDIT, 'Edit'),
        (CASE_EVENT_WORKING, 'Working'), #working on case?  this seems a bit ridiculous
        (CASE_EVENT_REOPEN, 'Reopen'), #case state
        (CASE_EVENT_COMMENT, 'Comment'),
        (CASE_EVENT_CUSTOM, 'Custom'), #custom are activities that don't resolve around the basic open/edit/view/resolve/close
        (CASE_EVENT_RESOLVE, 'Resolve'), #case status state
        (CASE_EVENT_CLOSE, 'Close'), #case status state
    )


STATUS_CHOICES = (
        (CASE_STATE_OPEN, 'Open'),
        (CASE_STATE_RESOLVED, 'Resolved'),
        (CASE_STATE_CLOSED, 'Closed'),
)

PRIORITY_LOW = 100
PRIORITY_MEDIUM = 500
PRIORITY_HIGH = 1000

PRIORITY_CHOICES = (
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
)
