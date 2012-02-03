from issuetracker.models import IssueEvent, Issue
from django.db.models.query_utils import Q
from datetime import timedelta, timedelta, datetime
from dimagi.utils.make_uuid import make_uuid
from django.utils.translation import ugettext_lazy as _
from django.db import models
from issuetracker import issue_constants
from issuetracker.models.issuecore import IssueCategory
from permissions.models import Actor

class Filter(models.Model):
    """

    """
    #below are the enumerated integer choices because integer fields don't like choices that aren't ints.
    #for more information see here:
    #http://www.b-list.org/weblog/2007/nov/02/handle-choices-right-way/
    TODAY = 0
    ONE_DAY = 1
    THREE_DAYS = 3
    ONE_WEEK = 7
    TWO_WEEKS = 14
    ONE_MONTH = 30
    TWO_MONTHS = 60
    THREE_MONTHS = 90
    SIX_MONTHS = 180
    ONE_YEAR = 365

    TIME_DURATION_FUTURE_CHOICES = (
        (-ONE_DAY, 'In the past day'),
        (TODAY, 'Today'),
        (ONE_DAY, 'Today or tomorrow'),
        (THREE_DAYS, 'In the next three days'),
        (ONE_WEEK, 'In the next week'),
        (TWO_WEEKS, 'In the next two weeks'),
        (ONE_MONTH, 'In the next month'),
        (TWO_MONTHS, 'In the next two months'),
        (THREE_MONTHS, 'In the next three months'),
        (SIX_MONTHS, 'In the next six months'),
        (ONE_YEAR, 'In the next year'),
    )

    TIME_DURATION_PAST_CHOICES = (
        (TODAY, 'Today'),
        (-ONE_DAY, 'Yesterday or today'),
        (-ONE_WEEK, 'In the past week'),
        (-ONE_MONTH, 'In the past month'),
        (-TWO_MONTHS, 'In the past two months'),
        (-THREE_MONTHS, 'In the past three months'),
        (-SIX_MONTHS, 'In the past six months'),
        (-ONE_YEAR, 'In the past year'),
    )
    id = models.CharField(_('Unique id'), max_length=32, unique=True, default=make_uuid, primary_key=True) #primary_key override?

    #metadata about the query
    description = models.CharField(max_length=64)
    creator = models.ForeignKey(Actor, related_name="filter_creator", null=True, blank=True)
    shared = models.BooleanField(default=False)


    custom_function=models.BooleanField(default=False)
    #Code based filter functions
    filter_module = models.CharField(max_length=128, blank=True, null=True,
                                      help_text=_("This is the fully qualified name of the module that implements the filter function."))

    filter_class = models.CharField(max_length=64, blank=True, null=True,
                                     help_text=_('This is the actual method name of the model filter you wish to run.'))

    #issue related properties
    category = models.ForeignKey(IssueCategory, null=True, blank=True)
    status = models.CharField(max_length=160, null=True, blank=True, choices=issue_constants.STATUS_CHOICES)
    priority = models.IntegerField(null=True, blank=True, choices=issue_constants.PRIORITY_CHOICES)

    opened_by = models.ForeignKey(Actor, null=True, blank=True, related_name="filter_opened_by")
    assigned_to = models.ForeignKey(Actor, null=True, blank=True, related_name="filter_assigned_to")
    last_edit_by = models.ForeignKey(Actor, null=True, blank=True, related_name="filter_last_edit_by")
    resolved_by = models.ForeignKey(Actor, null=True, blank=True, related_name="filter_resolved_by")
    closed_by = models.ForeignKey(Actor, null=True, blank=True, related_name="filter_closed_by")

    opened_date = models.IntegerField(choices=TIME_DURATION_PAST_CHOICES, null=True, blank=True)
    assigned_date = models.IntegerField(choices=TIME_DURATION_PAST_CHOICES, null=True, blank=True)
    last_edit_date = models.IntegerField(choices=TIME_DURATION_PAST_CHOICES, null=True, blank=True)
    resolved_date = models.IntegerField(choices=TIME_DURATION_PAST_CHOICES, null=True, blank=True)
    closed_date = models.IntegerField(choices=TIME_DURATION_PAST_CHOICES, null=True, blank=True)

    #issue Event information
    last_event_date = models.IntegerField(choices=TIME_DURATION_PAST_CHOICES, null=True, blank=True)
    last_event_by = models.ForeignKey(Actor, null=True, blank=True)


    def get_absolute_url(self):
        return '/filter/%s' % self.id

    #this should come in as a dictionary of key-value pairs that are compatible with a
    #django query when resolved as a kwargs.
    #http://stackoverflow.com/questions/310732/in-django-how-does-one-filter-a-queryset-with-dynamic-field-lookups
    #http://stackoverflow.com/questions/353489/cleaner-way-to-query-on-a-dynamic-number-of-columns-in-django

    def get_filter_queryset(self, requesting_actor):
        """
        On a given filter instance, we will generate a query set by applying all the FKs as query objects

        The return value is a queryset after applying all the query filters and doing a filter with
        the issue events as well.
        """
        utcnow = datetime.utcnow()

        issue_query_arr = []
        issue_event_query_arr = []

        if self.category:
            issue_query_arr.append(Q(category=self.category))
        if self.status:
            issue_query_arr.append(Q(status=self.status))
        if self.priority:
            issue_query_arr.append(Q(priority=self.priority))
        if self.assigned_to:
            if self.assigned_to.name == "Me":
                issue_query_arr.append(Q(assigned_to=requesting_actor))
            else:
                issue_query_arr.append(Q(assigned_to=self.assigned_to))

        if self.opened_by:
            if self.opened_by.name == "Me":
                issue_query_arr.append(Q(opened_by=requesting_actor))
            else:
                issue_query_arr.append(Q(opened_by=self.opened_by))
        if self.last_edit_by:
            if self.last_edit_by.name == "Me":
                issue_query_arr.append(Q(last_edit_by=requesting_actor))
            else:
                issue_query_arr.append(Q(last_edit_by=self.last_edit_by))
        if self.resolved_by:
            if self.resolved_by.name == "Me":
                issue_query_arr.append(Q(resolved_by=requesting_actor))
            else:
                issue_query_arr.append(Q(resolved_by=self.resolved_by))
        if self.closed_by:
            if self.closed_by.name == "Me":
                issue_query_arr.append(Q(closed_by=requesting_actor))
            else:
                issue_query_arr.append(Q(closed_by=self.closed_by))

        if self.opened_date:
            compare_date = utcnow + timedelta(days=self.opened_date)
            issue_query_arr.append(Q(opened_date__gte=compare_date))
        if self.assigned_date:
            compare_date = utcnow + timedelta(days=self.assigned_date)
            issue_query_arr.append(Q(assigned_date__gte=compare_date))
        if self.last_edit_date:
            compare_date = utcnow + timedelta(days=self.last_edit_date)
            issue_query_arr.append(Q(last_edit_date__gte=compare_date))
        if self.resolved_date:
            compare_date = utcnow + timedelta(days=self.resolved_date)
            issue_query_arr.append(Q(resolved_date__gte=compare_date))
        if self.closed_date:
            compare_date = utcnow + timedelta(days=self.closed_date)
            issue_query_arr.append(Q(closed_date__gte=compare_date))

        #ok, this is getting a little tricky.
        #query IssueEvent and we will get the actual issues.  we will get the id's of the issues and apply
        #those back as a filter
        if self.last_event_by:
            if self.last_event_by.name == "Me":
                issue_event_query_arr.append(Q(created_by=requesting_actor))
            else:
                issue_event_query_arr.append(Q(created_by=self.last_event_by))

        if self.last_event_date:
            compare_date = utcnow + timedelta(days=self.last_event_date)
            issue_event_query_arr.append(Q(created_date__gte=self.last_event_date))

        #now, we got the queries built up, let's run the queries
        issues = Issue.objects.select_related('opened_by', 'last_edit_by', 'resolved_by', 'closed_by', 'assigned_to', 'carteam_set').all()
        for qu in issue_query_arr:
            #dmyung 12-8-2009
            #doing the filters iteratively doesn't seem to be the best way.  there ought to be a way to chain
            #them all in an evaluation to the filter() call a-la the kwargs or something.  since these
            # are ANDED, we want them to be done sequentially (ie, filter(q1,q2,q3...)
            #negations should be handled by the custom search
            issues = issues.filter(qu)

        if len(issue_event_query_arr) > 0:
            issue_events = IssueEvent.objects.select_related().all()
            for qe in issue_event_query_arr:
                issue_events = issue_events.filter(qe)

            #get all the issue ids from the case event filters
            issue_events_issues_ids = issue_events.values_list('issue', flat=True)

            if len(issue_events_issues_ids) > 0:
                issues = issues.filter(pk__in=issue_events_issues_ids)

        return issues

    def __unicode__(self):
        return "Model Filter - %s" % (self.description)

    class Meta:
        app_label = 'issuetracker'
        #verbose_name = "Model Filter"
        #verbose_name_plural = "Model Filters"

    @property
    def get_gridpreference(self):
        if not hasattr(self, '_gridpreference'):
            self._gridpreference = self.gridpreference
        return self._gridpreference