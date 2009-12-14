# myapp/datagrids.py
from django.contrib.auth.models import User
from models import Case, CaseEvent, Filter, GridSort, GridColumn, GridOrder, GridPreference
from django.core.urlresolvers import reverse

from djblets.datagrid.grids import Column, DataGrid

class CaseDataGrid(DataGrid):    
    description = Column("Description", sortable = True, link=True, expand=True)            
    category = Column("Category", sortable = True, link=True)
    status = Column("Status", sortable = True, link=True)
    priority = Column("Priority", sortable = True)
    assigned_to = Column("Assigned to", sortable = True)
    opened_by = Column("Opened by", sortable = True)
    last_edit_by = Column("Last edit by", sortable = True)
    closed_by = Column("Closed by", sortable = True)
    resolved_by = Column("Resolved by", sortable = True)
    opened_date = Column("Opened date", sortable = True)
    last_edit_date = Column("Last edit date", sortable = True)
    resolved_date = Column("Resolved date", sortable = True)
    closed_date = Column("Closed date", sortable = True)
    next_action = Column("Next action", sortable = True)
    next_action_date = Column("Next action date", sortable = True)
    
    #these fields kill the datagrid query, it does an extra query for each item!
    #last_case_event= Column("Last event", sortable = True)
    #last_event_date = Column("Last event date", sortable = True)
    #last_event_by = Column("Last event by", sortable = True)
    
     
    def __init__(self, request, gridpref=None, qset = None, qtitle = None):        
        if gridpref:
            DataGrid.__init__(self, request, gridpref.filter.get_filter_queryset(), gridpref.filter.description)
        elif gridpref == None and qset != None:
            if qtitle == None:
                raise Exception("Error, if passing a queryset into the CaseDataGrid, you must provide some sort of title")
            DataGrid.__init__(self, request, qset, qtitle)
        else:                
            DataGrid.__init__(self, request, Case.objects.all(), "All cases")
            
        self.default_sort = ['opened_date']
        self.default_columns = ['description', 'category', 'opened_by', 'assigned_to', 'last_edit_date',]
     
    
    def link_to_object(self, obj, value):
        if isinstance(obj, Case):
            
            return reverse("casetracker.views.view_case", args=[obj.id])            
            #return reverse("view-case", args=[obj.id])
            
            
class CaseEventDataGrid(DataGrid):
    case = Column("Case", sortable = True)
            
    notes = Column("Notes", sortable = True)
    activity = Column("Activity", sortable = True)
    created_date = Column("created_date", sortable = True)
    created_by = Column("created_by", sortable = True)    
         
    def __init__(self, request, case_id=None):        
        if case_id:
            for_case = Case.objects.get(id=case_id)
            DataGrid.__init__(self, request, CaseEvent.objects.filter(case=for_case), "Events for case %s" % for_case.description)
            self.default_sort = ['-created_date']
            self.default_columns = ['notes', 'activity', 'created_date', 'created_by', ]
        else:
            DataGrid.__init__(self, request, CaseEvent.objects.all(), "All case events")
            self.default_sort = ['-created_date', 'case']
            self.default_columns = ['case', 'notes', 'activity', 'created_date', 'created_by', ]



class FilterDataGrid(DataGrid):    
    description = Column("Description", sortable = True, link=True, expand=True)            
    creator = Column("Creator", sortable=True, link=True)
    
    category = Column("Category", sortable = True, link=True)
    status = Column("Status", sortable = True, link=True)
    priority = Column("Priority", sortable = True)
    assigned_to = Column("Assigned to", sortable = True)
    opened_by = Column("Opened by", sortable = True)
    last_edit_by = Column("Last edit by", sortable = True)
    closed_by = Column("Closed by", sortable = True)
    resolved_by = Column("Resolved by", sortable = True)
    opened_date = Column("Opened date", sortable = True)
    last_edit_date = Column("Last edit date", sortable = True)
    resolved_date = Column("Resolved date", sortable = True)
    closed_date = Column("Closed date", sortable = True)
    next_action_date = Column("Next action date", sortable = True)
    
    #these fields kill the datagrid query, it does an extra query for each item!
    last_case_event= Column("Last event", sortable = True)
    last_event_date = Column("Last event date", sortable = True)
    last_event_by = Column("Last event by", sortable = True)
    
     
    def __init__(self, request, user=None):        
        if user:
            DataGrid.__init__(self, request, Filter.objects.filter(creator=user), "All filters for user %s" % user.username)
        else:
            DataGrid.__init__(self, request, Filter.objects.all(), "All filters")
                    
        self.default_sort = ['opened_date']
        self.default_columns = ['description', 'creator', 'category', 'opened_by', 'assigned_to', 'last_edit_date',]
     
    
    def link_to_object(self, obj, value):
        if isinstance(obj, Filter):       
            return reverse("casetracker.views.view_filter", args=[obj.id])            