from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from optparse import make_option
import sys
import os

from django.conf import settings
from django.core import serializers



class Command(BaseCommand):
    option_list = BaseCommand.option_list + (       
    )
    help = 'Register categories from the declarative caseregistry handler classes.'
    args = ""
 
    def handle(self, *scripts, **options):
        if not hasattr(settings, 'CASE_CATEGORIES'):
            raise Exception("Error, you don't have a CASE_CATEGORIES settings variable to define case types")
        
        for cat_str in settings.CASE_CATEGORIES:
            category_module = __import__(cat_str, {},{},[''])
            if hasattr(category_module, 'register_category'):
                register_method = getattr(category_module, 'register_category')
                print "found registration method for %s" % (category_module)
                register_method()
                print "registration complete"                
            
             
#        for cls in CategoryHandler.__subclasses__():
#            category_module = __import__(cls.__module__, {}, {}, [''])
#            if hasattr(category_module, 'register_category'):
#                register_method = getattr(category_module, 'register_category')
#                print "found registration method"
#                register_method()
#                print "registration complete"
#                print cls
#                print cls.__module__
            
            
        
            