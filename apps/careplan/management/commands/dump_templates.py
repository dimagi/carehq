from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from optparse import make_option
import sys
import os

from django.core import serializers
from careplan.models import TemplateCarePlan, PlanCategory, PlanTag, TemplateCarePlanItem



class Command(BaseCommand):
    option_list = BaseCommand.option_list
    help = 'Regenerate the CarePlan templates to json.'
    args = ""
 
    def handle(self, *scripts, **options):        
                
        models = [TemplateCarePlan, PlanCategory, PlanTag, TemplateCarePlanItem]
        
        
        all_data = []
        for model in models:
            fullset = model.objects.all()
            for item in fullset:
                all_data.append(item)
            
        outstring = serializers.serialize(queryset = all_data, format='json',indent=2)
        print outstring
                
        
            