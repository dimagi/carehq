from ashandapp.QueryGrid import QueryGridBase




class ProviderPatientGrid(QueryGridBase):    
    def __init__(self, *args, **kwargs):
        columns = ['description','assigned_to','last_event_by', 'last_event_date',]
        div_name='provider_pts'
        title='All Patient Cases'                
        QueryGridBase.__init__(self, div_name, title, columns=columns, *args, **kwargs)
        


class CaregiverPatientGrid(QueryGridBase):
    pass

class TriageCases(QueryGridBase):
    pass



class CareTeamActiveCases(QueryGridBase):
    pass

class CareTeamAllCases(QueryGridBase):
    pass

