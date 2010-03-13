from django import template
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.template import Context, Template

from casetracker.models import EventActivity, CaseEvent, Status, CaseAction
from datetime import datetime
register = template.Library() 
 
 
dirty_column_map = {
"description":"Description",
"category":"Category",
"status":"Status",
"priority":"Priority",

"assigned_to":"Assigned",
"opened_by":"Opened",
"last_edit_by":"Edited",
"resolved_by":"Resolved",
"closed_by":"Closed",

"opened_date":"Opened Date",
"last_edit_date":"Edit Date",
"resolved_date":"Resolved Date",
"closed_date":"Closed Date",

"next_action": "Next Action",
"next_action_date":"Due Date",
"last_case_event": "Last Event",
"last_event_date": "Event Date",
"last_event_by": "Last Event By",
}

@register.simple_tag 
def get_sType(case):
# BAD - hardcoded for only one instance. have to make smarter to detect time
    if pretty_column(case) == "Follow Up Date":
        return "\"pretty_time\""
    return "\"html\""

@register.simple_tag
def pretty_column(column):
    if dirty_column_map.has_key(column):
        return dirty_column_map[column]
    else:
        return column.replace("_","")
 
@register.simple_tag
def case_column(case, column):
    try:
        #return getattr(case,column)        
        data = getattr(case, column)
        
        if column == 'description':
            if case.category.slug == 'HomeMonitoring':
                return "[Home Monitor] %s" % (data)
            elif case.category.slug == 'System':
                return "[ASHand System] %s" % (data)

        
        
        datatype = data.__class__
        if datatype == datetime:
            if data > datetime.utcnow():
                timedelta_string = "timeuntil"
                time_suffix = "from now"
            else:
                timedelta_string = "timesince"
                time_suffix = "ago"
                
            t = Template("{{ dateval|%s:utcnow }}" % (timedelta_string))
            c = Context({"dateval": data, "utcnow":datetime.utcnow() })
            
            datastring = t.render(c).split(',')[0] + " " + time_suffix
            
        elif isinstance(data, User):
            datastring = "%s %s" % (data.first_name, data.last_name)
        elif isinstance (data, CaseAction):
            return data.description
        elif isinstance(data, CaseEvent):
            return data.activity.get_event_class_display()
        elif isinstance(data, Status):
            return data.get_state_class_display()
#        elif data == None and column == 'next_action_date':
#            return unicode(datetime.utcnow())             
        else:
            datastring = unicode(data)
        return datastring
    except Exception, e:
        raise Exception("Error rendering case column - the column '%s' does not exist on the object '%s': %s" % (column, case, e))