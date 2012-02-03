from actor_lifecycle_tests import *
from contrib_apps.django_digest.tests import TestCase


class actorObjectsTests(TestCase):

    def setUp(self):
        User.objects.all().delete()
        self.client = Client()
        self._createUser()

