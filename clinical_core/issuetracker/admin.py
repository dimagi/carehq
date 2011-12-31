from django.contrib import admin
from issuetracker.models import CaseEvent, Issue, Filter, GridPreference,GridColumn,GridOrder,GridSort



class EventActivityAdmin(admin.ModelAdmin):
    list_display=('past_tense','summary','event_class', 'past_tense', 'active_tense')
    list_filter = ['event_class']
    radio_fields = {
        'event_class': admin.HORIZONTAL,
    }

class CaseEventInline(admin.StackedInline):
    model = CaseEvent

class CaseAdmin(admin.ModelAdmin):
    list_display=('description','status','category', 'last_edit_by', 'last_edit_date','assigned_to')
    list_filter=['status','category','opened_by', 'last_edit_by','assigned_to']

    fieldsets = (
                 ('Basic Information', { 'fields': ('description',
                                                    ('category','status','priority'),
                                                    'body',
                                                    'assigned_to',
                                                    'parent_issue')
                                        }),
                 ('Activity Information', { 'fields': (('opened_by','opened_date'),
                                                       ('last_edit_by','last_edit_date'),
                                                       ('resolved_date','resolved_by'),
                                                       ('closed_date','closed_by'))
                                           })
                 )

    radio_fields = {"priority": admin.VERTICAL,
                    "category": admin.HORIZONTAL,
                    "status": admin.VERTICAL,
                    }
    inlines = [ CaseEventInline, ]


class CaseEventAdmin(admin.ModelAdmin):
    list_display=('id','notes','case','activity')
    list_filter = ['activity',]

class CaseInline(admin.StackedInline):
    model = Issue

class FilterAdmin(admin.ModelAdmin):
    list_display=('id','description','shared','creator')
    list_filter= ['shared','creator']
#    inlines=[GridPreferenceInline]
admin.site.register(Filter, FilterAdmin)

class ColumnSortInline(admin.TabularInline):
    model = GridSort

class ColumnOrderInline(admin.TabularInline):
    model = GridOrder

class GridColumnAdmin(admin.ModelAdmin):
    list_display= ('id','name', 'display', 'column_type', 'attribute')
    list_filter = ['column_type']
admin.site.register(GridColumn, GridColumnAdmin)

class GridPreferenceAdmin(admin.ModelAdmin):
    list_display= ('id','filter')
    inlines = [ColumnSortInline, ColumnOrderInline]
admin.site.register(GridPreference, GridPreferenceAdmin)

class GridSortAdmin(admin.ModelAdmin):
    list_display= ('id','preference','column','order','ascending')
admin.site.register(GridSort, GridSortAdmin)

class GridOrderAdmin(admin.ModelAdmin):
    list_display = ('id','preference','column','order')
    list_filter = ['preference']
admin.site.register(GridOrder, GridOrderAdmin)


admin.site.register(CaseEvent, CaseEventAdmin)
admin.site.register(Issue, CaseAdmin)
