import random
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from actorpermission.models import CHWActor, ProviderActor, CaregiverActor
from clinical_shared.middleware.identity import CareHQIdentityMiddleware
from clinical_shared.tests.testcase import CareHQClinicalTestCase
from clinical_shared.utils import generator
from clinical_shared.utils.scrambler import raddress
from permissions.models import Actor, Role, PrincipalRoleRelation
from permissions.tests import RequestFactory
from tenant.models import Tenant
from django.contrib.sessions.backends.file import SessionStore

class tenantPermissionTests(CareHQClinicalTestCase):
    def setUp(self):
        User.objects.all().delete()
        Actor.objects.all().delete()
        Role.objects.all().delete()
        PrincipalRoleRelation.objects.all().delete()
        Tenant.objects.all().delete()
        call_command('carehq_init')

    def testCreateActor(self, user=None, actor_type='chw'):
        """
        Create a User
        Make an actor for that user
        Verify actor counts
        """
        actor_docs_start = CHWActor.view('actorpermission/all_actors').count()
        actor_start = Actor.objects.all().count()

        tenant = Tenant.objects.all()[0]
        if user is None:
            user = generator.generate_random_user()

        if actor_type=='chw':
            actor_doc = self._new_chw(tenant, user)
        elif actor_type == 'provider' or actor_type=='external_provider':
            actor_doc = self._new_provider(tenant, user)
        elif actor_type == 'caregiver':
            actor_doc = self._new_caregiver(tenant,user)
        else:
            actor_doc = self._new_chw(tenant, user)

        #pact_api.add_chw(chw_actor)

        actor_docs_end = CHWActor.view('actorpermission/all_actors').count()
        actor_end = Actor.objects.all().count()

        self.assertEquals(actor_docs_start+1, actor_docs_end)
        self.assertEquals(actor_start+1, actor_end)

        #get the django actor from the DB
        django_actor = Actor.objects.get(id=actor_doc.actor_uuid)
        #make sure that the django actor is on the saved chw_actor
        self.assertEquals(django_actor, actor_doc.django_actor)

        couch_doc = CHWActor.view('actorpermission/all_actors', include_docs=True, key=actor_doc._id).first()
        self.assertEquals(couch_doc.first_name, actor_doc.first_name)
        self.assertEquals(couch_doc.last_name, actor_doc.last_name)
        self.assertEquals(couch_doc.title, actor_doc.title)

        #ensure that the post_load signal works too
        self.assertEquals(django_actor, couch_doc.django_actor)

        self.assertEquals(django_actor.doc_id, couch_doc._id)
        return actor_doc

    def testDeleteActor(self):
        actor_doc = self.testCreateActor()
        db = CHWActor.get_db()
        start_count = Actor.objects.all().count()

        doc_id = actor_doc._id

        django_actor = actor_doc.django_actor
        #django_actor = Actor.objects.get(id=actor_doc.actor_uuid)
        #actor_doc.delete()
        django_actor.delete()

        deprecated_doc = db.get(doc_id)
        end_count = Actor.objects.all().count()

        self.assertEquals(deprecated_doc['base_type'], 'DeletedBaseActorDocument')
        self.assertEquals(start_count, end_count+1)

    def testCreateUserMultipleActors(self):
        """
        Test to ensure that a single use with multiple actors can be identified with multiple actors.
        This also tests the identity middleware to attach the actors to the request object for a given user.
        """
        user = generator.generate_random_user()

        provider_types = ['chw','provider','caregiver','external_provider']

        provider_doc_ids = [self.testCreateActor(user, x)._id for x in provider_types]

        rf = RequestFactory()
        request = rf.get('/')
        request.session = SessionStore()
        request.user = user
        middleware = CareHQIdentityMiddleware()
        self.assertFalse(hasattr(request,'actors'))
        middleware.process_request(request)
        self.assertTrue(hasattr(request,'actors'))

        for m in request.actors:
            self.assertTrue(m.actordoc._id in provider_doc_ids)
        return user







