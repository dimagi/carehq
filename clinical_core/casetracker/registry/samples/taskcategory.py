from casetracker.registry import CategoryHandler

SLUG_PREFIX = 'task-'
CATEGORY_SLUG = 'task'
CATEGORY_DISPLAY = 'Task'
CATEGORY_DESCRIPTION = 'Basic Task Case Category'

class TaskCategory(CategoryHandler):
    category_slug = CATEGORY_SLUG
    category_display = CATEGORY_DISPLAY
    category_description = CATEGORY_DESCRIPTION
    custom_create = False
    custom_read = False

