from django import template
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from datetime import datetime
register = template.Library() 
 
@register.simple_tag
def case_column(case, column):
    try:
        #return getattr(case,column)        
        data = getattr(case, column)
        
        datatype = data.__class__
        if datatype == datetime:
            datastring = data.strftime("%m/%d/%Y")
        else:
            datastring = unicode(data)
        return datastring
    except Exception, e:
        raise Exception("Error rendering case column - the column '%s' does not exist on the object '%s': %s" % (column, case, e))