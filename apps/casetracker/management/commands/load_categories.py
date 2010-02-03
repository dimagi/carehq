from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from optparse import make_option
import sys
import os

from django.core import serializers
from casetracker.models import CaseAction, Category, Priority, Status, EventActivity



class Command(BaseCommand):
    option_list = BaseCommand.option_list + (       
    )
    help = 'Load categories from the declarative CategoryHandler subclasses.'
    args = ""
 
    def handle(self, *scripts, **options):        
        
        
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
                
        
            