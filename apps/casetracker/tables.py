import django_tables as tables
from casetracker.models import Case, Filter, GridPreference
#from django_tables.tables import Column, Table, ModelTable


#class CountryTable(Table):
#    name = tables.Column(verbose_name="Country Name")
#    population = tables.Column(sortable=False, visible=False)
#    time_zone = tables.Column(name="tz", default="UTC+1");
    
    
class CaseTable(tables.ModelTable):   
    
    def set_display(self, filterpref):
        #we need to create a display order array to call a order_by('column', '-other_column')
        ordering = [pref.sort_display for pref in GridPreference.objects.all()[0].gridpreference_sort.all().order_by('order')]
        self.queryset = filterpref.filter.get_filter_queryset().order_by(*ordering)
        #qset = filterpref.filter.get_filter_queryset().order_by(*ordering)        
        col_hash = {}
        for col in self.columns.all():
            col_hash[col.name] = col
            col.visible=False
            self.Meta.exclude.append(col.name)
        for col in filterpref.display_columns.all():
            #There is no error checking here because we want to do a hard exception to tell very quickly that a badly configured grid preference should be fixed
            #in particular, the name must be exactly matching.
            col_hash[col.name].visible = True
            pass
        
    
    def __init__(self, *args, **kwargs):               
        super(tables.ModelTable, self).__init__(*args, **kwargs)
        for col in self.columns.all():
            col.visible=False
            self.Meta.exclude.append(col.name)

        
                
    
    class Meta:
        model = Case
        exclude = ['orig_description', 'id']

    