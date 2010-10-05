from casetracker.registry import CategoryHandler

SLUG_PREFIX = 'system-'

CATEGORY_SLUG = 'system'
CATEGORY_DISPLAY = 'System'
CATEGORY_DESCRIPTION = 'Builtin System Messaging'

class SystemCategory(CategoryHandler):
    category_slug = CATEGORY_SLUG
    category_display = CATEGORY_DISPLAY
    category_description = CATEGORY_DESCRIPTION
    custom_create = False
    custom_read = False

