from django.core.management.base import BaseCommand
from optparse import make_option
from casetracker.models import ActivityClass
from casetracker import constants
from django.db import transaction


#   CASE_EVENT_CHOICES = (
#           (constants.CASE_EVENT_OPEN, 'Open/Create'), #case state
#           (constants.CASE_EVENT_VIEW, 'View'),
#           (constants.CASE_EVENT_EDIT, 'Edit'),
#           (constants.CASE_EVENT_REOPEN, 'Reopen'), #case state
#           (constants.CASE_EVENT_COMMENT, 'Comment'),
#           (constants.CASE_EVENT_RESOLVE, 'Resolve'), #case status state
#           (constants.CASE_EVENT_CLOSE, 'Close'), #case status state
#       )
#
#   slug = models.SlugField(unique=True) #from name
#   past_tense = models.CharField(max_length=64, help_text = "The past tense description of this activity") #from phrasing
#   active_tense = models.CharField(max_length=64, help_text = "The active tense of this activity - this text will be displayed as a button in the case view.") #present as button on case view
#   event_class = models.TextField(max_length=32, choices=CASE_EVENT_CHOICES, help_text = "The primitive class of this event.") # what class of event is it?
#   summary = models.CharField(max_length=255)


def make_activity(slug, past_tense, active_tense, event_class, summary):
    activity_class = ActivityClass(slug=slug,
                                  past_tense=past_tense,
                                  active_tense=active_tense,
                                  event_class=event_classs,
                                  summary=summary)
    activity_class.save()
    return activity_class


default_activites = [
    {
            "slug": "activity-open",
            "past_tense": "Created",
            "active_tense": "Create",
            "event_class": constants.CASE_EVENT_OPEN,
            "summary": "Create new case",
    },
    {
            "slug": "activity-view",
            "past_tense": "Viewed",
            "active_tense": "View",
            "event_class": constants.CASE_EVENT_VIEW,
            "summary": "View a case",
    },
    {
            "slug": "activity-edit",
            "past_tense": "Edited",
            "active_tense": "Edit",
            "event_class": constants.CASE_EVENT_EDIT,
            "summary": "Edit a case",
    },
    {
            "slug": "activity-reopen",
            "past_tense": "Reopened",
            "active_tense": "Reopen",
            "event_class": constants.CASE_EVENT_REOPEN,
            "summary": "Create new case",
    },
    {
            "slug": "activity-resolve",
            "past_tense": "Resolved",
            "active_tense": "Resolve",
            "event_class": constants.CASE_EVENT_RESOLVE,
            "summary": "Resolve a case",
    },
    {
            "slug": "activity-close",
            "past_tense": "Closed",
            "active_tense": "Close",
            "event_class": constants.CASE_EVENT_CLOSE,
            "summary": "Close a case",
    },
]



class Command(BaseCommand):
   option_list = BaseCommand.option_list + (
       make_option('--clean', action='store_true',
               dest='clean_db', default=False,
               help='Override, blow away the Category tables and start anew.'),
   )
   help = 'Load default case ActivityClass, extend and replace system states here.'


   @transaction.commit_manually
   def handle(self, *scripts, **options):
        if options.get('clean_db'):
           #not for the faint of heart, this blows away everything
           ActivityClass.objects.all().delete()

        for activity_dict in default_activites:
            activity_class = ActivityClass(activity_dict['slug'],
                                          activity_dict['past_tense'],
                                          activity_dict['active_tense'],
                                          activity_dict['event_class'],
                                          activity_dict['summary'])
            activity_class.save()
            print "Saved activity: %s" % (activity_class.slug)

        transaction.commit()
        print "\n\nRegistered Activities: %d" % (ActivityClass.objects.all().count())



