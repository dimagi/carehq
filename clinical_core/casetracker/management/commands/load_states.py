from django.core.management.base import BaseCommand
from optparse import make_option
from casetracker.models import  Status
from casetracker.models import CASE_STATES
from django.db import transaction


def make_status(slug, display, state_class):
    newstatus = Status(slug=slug,
                    display=display,
                    state_class = state_class)
    newstatus.save()
    return newstatus


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--clean', action='store_true',
                dest='clean_db', default=False,
                help='Override, blow away the Category tables and start anew.'),
    )
    help = 'Load default case Status codes, extend and replace system states here.'


    def handle(self, *scripts, **options):
        if options.get('clean_db'):
            #not for the faint of heart, this blows away everything
            Status.objects.all().delete()

        active = make_status("status-open",
                            "Open",
                            CASE_STATES[0][0])
        print "Saved status: %s" % (active.slug)


        resolved = make_status("status-resolved",
                        "Resolved",
                        CASE_STATES[1][0])
        print "Saved status: %s" % (resolved.slug)


        closed = make_status("status-closed",
                        "Closed",
                        CASE_STATES[2][0])
        closed.save()

        print "Saved status: %s" % (closed.slug)


        print "\n\nRegistered Status Instances: %d" % (Status.objects.all().count())



