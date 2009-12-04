from django.core.management import call_command
call_command('loaddata', '0-caseaction.json')
call_command('loaddata', '1-category.json')
call_command('loaddata', '2-eventactivity.json')
call_command('loaddata', '3-priority.json')
call_command('loaddata', '4-status.json')