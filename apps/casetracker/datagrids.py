# myapp/datagrids.py
from django.contrib.auth.models import User
from models import Case, CaseEvent, Filter, GridSort, GridColumn, GridOrder, GridPreference
from djblets.datagrid.grids import Column, DataGrid

class CaseDataGrid(DataGrid):
    description = Column("Description", sortable = True)
            
    category = Column("Category", sortable = True)
    status = Column("Status", sortable = True)
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
    
    last_case_event= Column("Last event", sortable = True)
    last_event_date = Column("Last event date", sortable = True)
    last_event_by = Column("Last event by", sortable = True)
    
     
    def __init__(self, request, gridpref=None):        
        if gridpref:
            DataGrid.__init__(self, request, gridpref.filter.get_filter_queryset(), gridpref.filter.description)
        else:
            DataGrid.__init__(self, request, Case.objects.all(), "All cases")
                    
        DataGrid.__init__(self, request, Case.objects.all(), "All cases")
        self.default_sort = ['opened_date']
        self.default_columns = ['case_title', 'category', 'opened_by', 'assigned_to', 'last_edit_date', 'last_event_date']
            
class CaseEventDataGrid(DataGrid):
    case = Column("Case", sortable = True)
            
    notes = Column("Notes", sortable = True)
    activity = Column("Activity", sortable = True)
    created_date = Column("created_date", sortable = True)
    created_by = Column("created_by", sortable = True)    
         
    def __init__(self, request, for_case=None):        
        if for_case:
            DataGrid.__init__(self, request, CaseEvent.objects.filter(case=for_case), "Events for case %s" % for_case.description)
            self.default_sort = ['-created_date']
            self.default_columns = ['notes', 'activity', 'created_date', 'created_by', ]
        else:
            DataGrid.__init__(self, request, CaseEvent.objects.all(), "All case events")
            self.default_sort = ['-created_date', 'case']
            self.default_columns = ['case', 'notes', 'activity', 'created_date', 'created_by', ]
