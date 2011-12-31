#from django.test import TestCase
#from issuetracker.models import Category
#from issuetracker.registry.handler import CategoryHandler
#from django.core.management import call_command
#
#class CategoryVerificationTest(TestCase):
#    fixtures = ['samplesetup-fixture.json']
#    def setUp(self):
#        pass
#
#    def testVerifyHandlerProperties(self):
#        """
#        Verify that the handler property has at least all the FIELD properties of the Category class moving forward.
#        """
#        category_class = Category
#        handler_class = CategoryHandler
#        fields = category_class._meta.fields
#        for f in fields:
#            name = f.name
#            if f.name == "id":
#                continue
#            handler_property = "category_%s" % (name)
#            has_attr = hasattr(handler_class, handler_property)
#            print "Verifying handler property %s: %s" % (handler_property, has_attr)
#            self.assertTrue(has_attr)
#
