from django import template
from django.core.urlresolvers import reverse
 
register = template.Library() 
 
@register.simple_tag
def case_column(case, column):
    try:
        return getattr(case, column)
    except:
        raise Exception("Error rendering case column - the column '%s' does not exist on the object '%s'" % (column, case))