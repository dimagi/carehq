from django.core.management import call_command
from casetracker.models import Category, Status
from casetracker import constants 

def load_fixtures():
    """
    Basic fixtures necessary for ASHand to run
    """
    call_command('loaddata', '0-caseaction.json')
    call_command('loaddata', '1-category.json')
    call_command('loaddata', '2-eventactivity.json')
    call_command('loaddata', '3-priority.json')
    #call_command('loaddata', '4-status.json') # switching to autogenerate the different status.
    
    states = {"Active/Open (default)": constants.CASE_STATE_OPEN, "Resolved (default)": constants.CASE_STATE_RESOLVED, "Closed (default)": constants.CASE_STATE_CLOSED}
    for cat in Category.objects.all():
        for desc, cls in states.items():
            status = Status()
            status.description = desc
            status.category = cat
            status.state_class = cls
            status.save()
        print "\tSaving default states for category: %s" % (cat) 
        
    print "Created case state models"
    
    call_command('loaddata', '5-gridcolumns.json')
    call_command('loaddata', 'build-example_filters.json')
        
    call_command('loaddata', 'demo-identifiers.json')    
    call_command('loaddata', 'careplan-templates.json')
    
    
    
def run():
    load_fixtures()