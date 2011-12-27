import random
import uuid
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.test.testcases import TransactionTestCase
from actorpermission.models.actortypes import CHWActor, ProviderActor, CaregiverActor
from carehq_core import carehq_api
from carehqadmin.forms.provider_form import ProviderForm
from clinical_shared.middleware.identity import CareHQIdentityMiddleware
from clinical_shared.utils import generator
from clinical_shared.utils.scrambler import raddress
from pactcarehq.views.providers import pt_new_or_link_provider
from patient.models.patientmodels import Patient
from permissions.models import Actor, Role, PrincipalRoleRelation
from permissions.tests import RequestFactory
from tenant.models import Tenant
from django.contrib.sessions.backends.file import SessionStore

class migratePactInPlaceTests(TransactionTestCase):
    """
    Upgrade old style pact Actor documents in place to use unified carehq actor types.
    """

    def setUp(self):
        User.objects.all().delete()
        Actor.objects.all().delete()
        Role.objects.all().delete()
        Tenant.objects.all().delete()
        PrincipalRoleRelation.objects.all().delete()
        call_command('pact_init')
        call_command('carehq_init')
        self.tenant = Tenant.objects.all()[0]

    def _new_provider_oldstyle(self, tenant, first_name, last_name):
        #django_actor.name = '%s-%s-%s_%s' % (tenant.prefix, self.__class__.__name__, self.first_name, self.last_name)
        actor = Actor()
        old_class = 'ProviderActor'
        actor.name = '%s-%s-%s_%s' % (tenant.prefix, old_class, first_name, last_name)
        actor.save()
        return actor

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
        provider_actor.provider_title = generator.random_word(length=12)
        provider_actor.email = "%s@%s.com" % (generator.random_word(length=8), generator.random_word(length=8))
        provider_actor.facility_name = generator.random_word(length=12)
        provider_actor.facility_address = generator.random_text(length=12)
        provider_actor.save(tenant, user=user)
        return provider_actor

    def _new_caregiver(self, tenant, user):
        caregiver_actor = CaregiverActor()
        caregiver_actor.phone_number = str(generator.random_number(length=11))
        caregiver_actor.relation = random.choice(CaregiverActor.RELATIONSHIP_CHOICES)[0]
        caregiver_actor.address = raddress()
        caregiver_actor.save(tenant, user=user)
        return caregiver_actor


    def testCreateActorInView(self):
        """
        Call view function directly for API testing verification
        """
        start_prr = PrincipalRoleRelation.objects.count()
        user = generator.generate_random_user()
        patient = generator.get_or_create_patient(self.tenant, user=None, first_name="Jean-luc", last_name="Picard")
        form_data= {'phone_number': u'6171234567', 'first_name': u'Gregory', 'last_name': u'House',
                    'title': u'Dr.', 'facility_name': u'Princeton General', 'notes': u'Mock Made', 'provider_title': u'Diagnostician',
                    'facility_address': u'erdfb3245', 'email': u'cxvbxvcb'}


        rf = RequestFactory()
        request = rf.get('/')
        request.session = SessionStore()
        request.user = user
        request.POST=form_data
        request.method="POST"
        resp = pt_new_or_link_provider(request, patient._id)

        end_prr = PrincipalRoleRelation.objects.count()
        self.assertEqual(start_prr+2, end_prr)

        local_prrs = PrincipalRoleRelation.objects.filter(content_type=ContentType.objects.get_for_model(Patient))
        self.assertEqual(local_prrs.count(), 1)

        general_prrs = PrincipalRoleRelation.objects.filter(content_type=None)
        self.assertEqual(general_prrs.count(), 1)

    def testCreateAndFixOldActor(self, user=None, actor_type='chw'):
        """
        Create old style actor with no user (external provider)
        """

        start_prr = PrincipalRoleRelation.objects.count()
        patient = generator.get_or_create_patient(self.tenant, user=None, first_name="Jean-luc", last_name="Picard")

        actor = self._new_provider_oldstyle(self.tenant, "Dr. Gregory", "House")
        form_data= {'phone_number': u'6171234567', 'first_name': u'Gregory', 'last_name': u'House',
              'title': u'Dr.', 'facility_name': u'Princeton General', 'notes': u'Mock Made', 'provider_title': u'Diagnostician',
              'facility_address': u'erdfb3245', 'email': u'cxvbxvcb'}


        form = ProviderForm(self.tenant, data=form_data)
        if form.is_valid():
            provider_actor = form.save(commit=False)
            provider_actor.django_actor = actor
            provider_actor._id = uuid.uuid4().hex
            actor.doc_id = provider_actor._id

            actor.save()
            provider_actor.save(self.tenant)
            carehq_api.add_external_provider_to_patient(patient, provider_actor)

        end_prr = PrincipalRoleRelation.objects.count()
        self.assertEqual(start_prr+2, end_prr)

        local_prrs = PrincipalRoleRelation.objects.filter(actor=actor).filter(content_type=ContentType.objects.get_for_model(Patient))
        self.assertEqual(local_prrs.count(), 1)

        general_prrs = PrincipalRoleRelation.objects.filter(actor=actor).filter(content_type=None)
        self.assertEqual(general_prrs.count(), 1)

        #next now, let's adjust the naming convention
        actors = Actor.objects.all()
        for a in actors:
            django_doc = a.actordoc
            new_name = django_doc.get_actor_djangoname(self.tenant)
            self.assertNotEqual(a.name, new_name)
            a.name = new_name
            a.save()


