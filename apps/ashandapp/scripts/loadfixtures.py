from django.core.management import call_command
from casetracker.models import Category, Status
from casetracker import constants 

def do_load_fixtures():
    """
    Basic fixtures necessary for ASHand to run
    """
    call_command('loaddata', 'example-priority.json')
    call_command('loaddata', 'example-gridcolumns.json')
#    call_command('loaddata', 'example-filters.json')
        
    call_command('loaddata', 'demo-identifiers.json')    
 #   call_command('loaddata', 'careplan-templates.json')
    
    #call_command('register_categories') #this ought to be called as a separate command    
    
def run():
    do_load_fixtures()