from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from optparse import make_option
import sys
import os

from django.core import serializers
from casetracker.models import CaseAction, Category, Priority, Status, EventActivity, GridColumn



class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--splitfiles', action='store_true', dest='splitfiles', default=True,
            help='Split each model into individual files (default=True)'),       
        make_option('--single', action='store_true', dest='single', default=False,
            help='Combine serialized output to one file (default=False)'),
        make_option('--prefix', action='store_true', dest='output_prefix', default=False,
            help='Prefix for output file(s)'),
        make_option('--stdout', '--silent', action='store_true', dest='stdout', default=False,
            help='Print to stdout, will override all split and prefix settings'),
       
    )
    help = 'Runs a script in django context.'
    args = "script [script ...]"
 
    def handle(self, *scripts, **options):        
        splitfiles = options.get('splitfiles')
        single = options.get('single')
        if single: #nasty little exclusion hack
            splitfiles = False
        
        if options.get('prefix'):
            prefix = options.get('prefix')
        else:
            prefix = "fixtures-"
        
        if options.get('stdout'):
            print_stdout = options.get('stdout')
            splitfiles = False
        else:
            print_stdout = False
        
        models = [CaseAction,Category,Priority,Status,EventActivity, GridColumn]
        
        if print_stdout or (not splitfiles):
            all_data = []
            for model in models:
                fullset = model.objects.all()
                for item in fullset:
                    all_data.append(item)
            
            outstring = serializers.serialize(queryset = all_data, format='json',indent=2)
            if print_stdout:
                print outstring
            else:
                fout = open(prefix + 'alldata.json', 'w')
                fout.write(outstring)
                fout.close()
                print "outputted %s" % (prefix+'alldata.json')
        
        if splitfiles:        
            for model in models:
                model_data = model.objects.all() 
                outstring = serializers.serialize(queryset = model_data, format='json',indent=2)
                fout = open(prefix + model.__name__.lower() + '.json', 'w')
                fout.write(outstring)
                fout.close()
                print "outputted %s" % (prefix + model.__name__.lower() + '.json')
                
        
            