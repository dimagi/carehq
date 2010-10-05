from django.test import TestCase
from casetracker.models.casecore import Category
from casetracker.registry.handler import CategoryHandler
from django.core.management import call_command

class CategoryVerificationTest(TestCase):
    def setUp(self):
        call_command('load_categories', '--clean')
        call_command('load_states', '--clean')
        call_command('load_activities', '--clean')
        call_command('loaddata', 'default-priority.json')

    def testVerifyHandlerProperties(self):
        """
        Verify that the handler property has at least all the FIELD properties of the Category class moving forward.
        """
        category_class = Category
        handler_class = CategoryHandler
        fields = category_class._meta.fields
        for f in fields:
            name = f.name
            if f.name == "id":
                continue
            handler_property = "category_%s" % (name)
            has_attr = hasattr(handler_class, handler_property)
            print "Verifying handler property %s: %s" % (handler_property, has_attr)
            self.assertTrue(has_attr)

