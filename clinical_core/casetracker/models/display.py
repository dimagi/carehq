from django.db import models
from django.utils.translation import ugettext_lazy as _
from casecore import Filter
from clincore.utils import make_uuid


class GridColumn(models.Model):
    """
    The gridcolumn is the main, flat store for all columns that could be used in a grid.
    
    It's flat, the name of the column is directly used in the Case column selector and sort criteria.
    So there's no need for namespacing it or anything like that.  If it's named something, it'll exist here.
    
    In other words, the GridColumn's name MUST be a property of case and casefilter for it to be useful.
    """
    
    GRIDCOLUMN_CHOICES = (
                          ('case_field', "Case Field"),
                          ('related_field',"Related Field"),
                          ('custom_func',"Custom Function Call"),
                          )
    name = models.SlugField(max_length=32, unique=True)
    display = models.CharField(max_length=64, null=True, blank=True)
    column_type = models.CharField(max_length=16, choices=GRIDCOLUMN_CHOICES, default=GRIDCOLUMN_CHOICES[0][0], null=True, blank=True)
    attribute = models.CharField(max_length=160, null=True, blank=True)
    
    class Meta:
        app_label = 'casetracker'
        ordering = ('name',)
        
    def __unicode__(self):
        return self.name
    
    def get_column_value(self, case):
        """
        TODO: do the getattr() off the case if it's a case_field, else, if it's related or custom field, do some magic
        """
        return None


class GridSort(models.Model):
    """
    When a grid preference FKs to a GridColumn, this through model will tell how to represent it
    when using the column as a sorting column.  In representation it'll be either be name or -name.
    
    The gridcolumn presents the actual case property of the Case queryset you pass into the ordering() method.
    The filter queryset will be built using these strings.
    """
    column = models.ForeignKey("GridColumn", related_name='gridcolumn_sort')
    preference = models.ForeignKey("GridPreference", related_name="gridpreference_sort")
    ascending = models.BooleanField()
    display_split = models.BooleanField(default=False)
    order = models.PositiveIntegerField()
    
    @property
    def sort_display(self):
        if self.ascending:
            return self.column.name
        else:
            return "-%s" % self.column.name
    def __unicode__(self):
        if self.ascending:
            ascend = "ascending"
        else:
            ascend = "descending"
        return "GridSort - %s %s" % (self.column, ascend)
    
    
    class Meta:
        app_label = 'casetracker'
        verbose_name = "Grid column sort ordering"
        verbose_name_plural = "Grid column sort order definitions"
        ordering = ['order']
    



class GridOrder (models.Model):
    """
    When a grid preference FKs to a GridColumn, this through model will tell how to represent it
    when using the column as a column for display.  This tells us which columns will be arranged in what order
    for display on the data table.
    
    The gridcolumn presents the actual Case queryset properties to actually render in the order they are reprsented
    in this through model.
    """
    column = models.ForeignKey("GridColumn", related_name='gridcolumn_displayorder')
    preference = models.ForeignKey("GridPreference", related_name="gridpreference_displayorder")
    order = models.PositiveIntegerField()
    
    class Meta:
        app_label = 'casetracker'
        verbose_name = "Grid column display ordering"
        verbose_name_plural = "Grid column display order definitions"
        ordering = ['order']
    def __unicode__(self):
        return "%d - %s" % (self.order, self.column.name)
    

class GridPreference(models.Model):
    """
    A filter will have a one to one mapping to this model for showing how to display the given grid.    
    """
    id = models.CharField(_('Unique id'), max_length=32, unique=True, editable=False, default=make_uuid, primary_key=True) #primary_key override?
    filter = models.OneToOneField(Filter, related_name='gridpreference') #this could be just a foreign key and have multiple preferences to a given filter.
    
    display_columns = models.ManyToManyField(GridColumn, through=GridOrder, related_name="display_columns")
    sort_columns = models.ManyToManyField(GridColumn, through=GridSort, related_name="sort_columns")
        
    def __unicode__(self):
        return "Grid Display Preference: %s" % self.filter.description    
    
    class Meta:
        app_label = 'casetracker'
        verbose_name = "Filter Grid Display Preference"
        verbose_name_plural = "Filter Grid Display Preferences"
        ordering = ['filter']
        
    @property
    def get_display_columns(self):
        """
        returns the display columns in order of the through class's definition
        """        
        if not hasattr(self, '_display_columns'):
            self._display_columns = self.gridpreference_displayorder.all().select_related()
        return self._display_columns 
    
    @property
    def get_sort_columns(self):
        """
        Returns the display columns in order of the through class's definition
        """
        col_sort_orders = self.gridpreference_sort.all().values_list('column__id', flat=True)
        return GridColumn.objects.select_related().all().filter(id__in=col_sort_orders)    
    
    @property
    def get_sort_columns_raw(self):
        """
        returns the display columns in order of the through class's definition
        """
        col_sort_orders = self.gridpreference_sort.all().select_related()
        
        return [x.sort_display for x in col_sort_orders]    
    
    @property
    def get_colsort_jsonarray(self):
        #"aaSorting": [ [0,'asc'], [1,'asc'] ],
        if not hasattr(self, '_sort_json'):                
            cols = list(self.get_display_columns)
            sorts = self.gridpreference_sort.all()
            ret = []
            for s in sorts:
                idx = cols.index(s.column)
                if s.ascending == 1:
                    ret.append([idx + 1, 'asc'])
                else:
                    ret.append([idx + 1, 'desc'])
            
            self._sort_json = ret        
        return self._sort_json
