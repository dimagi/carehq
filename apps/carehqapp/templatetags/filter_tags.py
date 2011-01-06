from django import template
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.contrib.auth.models import User

from casetracker.models import  CaseEvent, Status
from datetime import datetime
from casetracker.models.casecore import Case
from patient.models.djangomodels import Patient
from actors.models.actors import Actor

register = template.Library()

 
#dirty_column_map = {
#"patient":"Patient",
#"description":"Description",
#"category":"Category",
#"status":"Status",
#"priority":"Priority",
#
#"assigned_to":"Assigned",
#"opened_by":"Opened",
#"last_edit_by":"Edited",
#"resolved_by":"Resolved",
#"closed_by":"Closed",
#
#"opened_date":"Opened Date",
#"last_edit_date":"Edit Date",
#"resolved_date":"Resolved Date",
#"closed_date":"Closed Date",
#
#"next_action": "Next Action",
#"next_action_date":"Due Date",
#"last_case_event": "Last Event",
#"last_event_date": "Event Date",
#"last_event_by": "Last Event By",
#}

#column_types = {
#"patient":"html",
#"description":"html",
#"category":"html",
#"status":"html",
#"priority":"html",
#
#"assigned_to":"html",
#"opened_by":"html",
#"last_edit_by":"html",
#"resolved_by":"html",
#"closed_by":"html",
#
#"opened_date":"pretty_time",
#"last_edit_date":"pretty_time",
#"resolved_date":"pretty_time",
#"closed_date":"pretty_time",
#
#"last_case_event": "html",
#"last_event_date": "pretty_time",
#"last_event_by": "html",
#}




#
#def get_column_types(column_names):
#    ret = []
#    for name in column_names:
#        ret.append({'sType': column_types[name]})
#    return ret

#@register.simple_tag 
#def get_sType(col_name):
## BAD - hardcoded for only one instance. have to make smarter to detect time
#    if pretty_column(col_name) == "Follow Up Date":
#        return "\"pretty_time\""
#    return "\"html\""

#@register.simple_tag
#def pretty_column(column):
#    if dirty_column_map.has_key(column):
#        return dirty_column_map[column]
#    else:
#        return column.replace("_","")
 
 
@register.simple_tag
def render_filter_heading(heading_object):
    #return "Some heading: %s" % heading_object.get_absolute_url()

    if isinstance(heading_object, Case):
        return "<h3>Category: %s</h3>" % heading_object.display
    elif isinstance(heading_object,Patient):
        return "<h3>%s</h3>" % heading_object.full_name
    elif isinstance(heading_object, Actor):
        return "<h3>By: %s</h3>" % heading_object.title
    elif isinstance(heading_object, Status):
        return "some status"
    else:
        return ""

 
@register.simple_tag
def case_column_plain(case, column):
    #print column
    return render_case_column(case, column, plain_text=False)    
    
def render_case_column(case, gridorder, plain_text=True):    
    column = gridorder.column.name
    try:
        if column == 'patient':
            data = case.patient
        else:        
            data = getattr(case, column)
                
        datatype = data.__class__
        if datatype == datetime:
#            if data > datetime.utcnow():
#                timedelta_string = "timeuntil"
#                time_suffix = "from now"
#            else:
#                timedelta_string = "timesince"
#                time_suffix = "ago"
#                
#            t = Template("{{ dateval|%s:utcnow }}" % (timedelta_string))
#            c = Context({"dateval": data, "utcnow":datetime.utcnow() })
#            
#            datastring = t.render(c).split(',')[0] + " " + time_suffix
##            datastring = str(data)
            datastring = '<abbr class="timeago" title="%s"></abbr>' % data.strftime("%Y-%m-%dT%H:%M:%SZ")

        elif isinstance(data, Patient):
            datastring = data.full_name
        elif isinstance(data, Case):
            datastring = data.doc_type
        elif isinstance(data, Actor):
            #print "is a freaking user: "  + str(data)
            #datastring = '<a href="%s">%s</a>' % (reverse('carehqapp.views.users.single', kwargs={'user_id': data.id}), data.get_full_name())
            datastring = data.title
        elif isinstance(data, CaseEvent):
            return data.activity.get_event_class_display()
        elif isinstance(data, Status):
            return data.get_state_class_display()
        elif isinstance(data, unicode) or isinstance(data, str):            
            if column == 'description':
                if case.category.slug == 'HomeMonitoring':
                    datastring =  "[Home Monitor] %s" % (data)
                elif case.category.slug == 'System':
                    datastring = "[ASHand System] %s" % (data)
                else:
                    datastring = unicode(data)                    
                if not plain_text:
                    tmp = '<a href="%s">%s</a>' % (reverse('manage-case', kwargs={'case_id':case.id}), datastring)
                    datastring = tmp
        else:
            datastring = unicode(data)        
        return datastring
    except Exception, e:
        raise Exception("Error rendering case column - the column '%s' does not exist on the object '%s': %s" % (column, case, e))