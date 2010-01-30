from django.core.management import call_command

def load_fixtures():
    """
    Basic fixtures necessary for ASHand to run
    """
    call_command('loaddata', '0-caseaction.json')
    call_command('loaddata', '1-category.json')
    call_command('loaddata', '2-eventactivity.json')
    call_command('loaddata', '3-priority.json')
    call_command('loaddata', '4-status.json')
    call_command('loaddata', '5-gridcolumns.json')
    call_command('loaddata', 'build-example_filters.json')
        
    call_command('loaddata', 'demo-identifiers.json')    
    call_command('loaddata', 'careplan-templates.json')
    
    
    
def run():
    load_fixtures()