import pdb
import random
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test.testcases import TransactionTestCase
from actorpermission.models.actortypes import CHWActor, ProviderActor, CaregiverActor
from clinical_shared.middleware.identity import CareHQIdentityMiddleware
from clinical_shared.utils import generator
from clinical_shared.utils.scrambler import raddress
from permissions.models import Actor, Role
from permissions.tests import RequestFactory
from tenant.models import Tenant
from django.contrib.sessions.backends.file import SessionStore

class tenantPermissionTests(TransactionTestCase):
    def setUp(self):
        User.objects.all().delete()
        Actor.objects.all().delete()
        Role.objects.all().delete()
        call_command('carehq_init')

    def _new_chw(self, tenant, user):
        chw_actor = CHWActor()
        chw_actor.first_name = user.first_name
        chw_actor.last_name = user.last_name
        chw_actor.title = "Mock CHW"
        chw_actor.phone_number = generator.random_number()
        chw_actor.save(tenant, user=user)
        return chw_actor
    def _new_provider(self, tenant, user):
        provider_actor = ProviderActor()
        provider_actor.provider_title=generator.random_word(length=12)
        provider_actor.email= "%s@%s.com" % (generator.random_word(length=8), generator.random_word(length=8))
        provider_actor.facility_name = generator.random_word(length=12)
        provider_actor.facility_address = generator.random_text(length=12)
        provider_actor.save(tenant, user=user)
        return provider_actor

    def _new_caregiver(self, tenant, user):
        caregiver_actor = CaregiverActor()
        caregiver_actor.phone_number=str(generator.random_number(length=11))
        caregiver_actor.relation = random.choice(CaregiverActor.RELATIONSHIP_CHOICES)[0]
        caregiver_actor.address=raddress()
        caregiver_actor.save(tenant, user=user)
        return caregiver_actor

    def testCreateActor(self, user=None, actor_type='chw'):
        """
        Create a User
        Make an actor for that user
        Verify actor counts
        """
        db = CHWActor.get_db()

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







