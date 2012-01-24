#system constants
SYSTEM_USERNAME='ASHand-System'

#constants for model Status
#CASE_STATE_NEW = 'state-new' # a state-new case is one that is brand new and unassigned, needing triageing.
ISSUE_STATE_OPEN = 'state-open'
ISSUE_STATE_RESOLVED = 'state-resolved'
ISSUE_STATE_CLOSED = 'state-closed'


#constants for case event activities
ISSUE_EVENT_OPEN = 'event-open'
ISSUE_EVENT_VIEW = 'event-view'
ISSUE_EVENT_EDIT = 'event-edit'
ISSUE_EVENT_ASSIGN = 'event-assign'
ISSUE_EVENT_WORKING = 'event-working'
ISSUE_EVENT_COMMENT = 'event-comment'
ISSUE_EVENT_CUSTOM = 'event-custom'

ISSUE_EVENT_REOPEN = 'event-reopen'
ISSUE_EVENT_RESOLVE = 'event-resolve'
ISSUE_EVENT_CLOSE = 'event-close'


CASE_EVENT_CHOICES = (
        (ISSUE_EVENT_OPEN, 'Open/Create'), #case state
        (ISSUE_EVENT_VIEW, 'View'),
        (ISSUE_EVENT_EDIT, 'Edit'),
        (ISSUE_EVENT_WORKING, 'Working'), #working on case?  this seems a bit ridiculous
        (ISSUE_EVENT_REOPEN, 'Reopen'), #case state
        (ISSUE_EVENT_COMMENT, 'Comment'),
        (ISSUE_EVENT_CUSTOM, 'Custom'), #custom are activities that don't resolve around the basic open/edit/view/resolve/close
        (ISSUE_EVENT_RESOLVE, 'Resolve'), #case status state
        (ISSUE_EVENT_CLOSE, 'Close'), #case status state
    )


STATUS_CHOICES = (
        (ISSUE_STATE_OPEN, 'Open'),
        (ISSUE_STATE_RESOLVED, 'Resolved'),
        (ISSUE_STATE_CLOSED, 'Closed'),
)
STATUS_RESOLVE_CHOICES = (
    (ISSUE_STATE_RESOLVED, 'Resolved'),
    )

STATUS_CLOSE_CHOICES = (
    (ISSUE_STATE_CLOSED, 'Closed'),
        )

STATUS_REOPEN_CHOICES = (
    (ISSUE_STATE_OPEN, 'Open'),
    )

PRIORITY_LOW = 100
PRIORITY_MEDIUM = 500
PRIORITY_HIGH = 1000

PRIORITY_CHOICES = (
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
)
