import random
import uuid
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.test.testcases import TestCase
from carehqadmin.forms.provider_form import ProviderForm
from clinical_shared.middleware.identity import CareHQIdentityMiddleware
from clinical_shared.tests.testcase import CareHQClinicalTestCase
from clinical_shared.utils import generator
from clinical_shared.utils.scrambler import raddress
from patient.models import Patient
from permissions.models import Actor, Role, PrincipalRoleRelation
from permissions.tests import RequestFactory
from tenant.models import Tenant
from django.contrib.sessions.backends.file import SessionStore
from actorpermission.models import CHWActor, ProviderActor, CaregiverActor
from carehq_core import carehq_api

class migratePactInPlaceTests(CareHQClinicalTestCase):
    """
    Upgrade old style pact Actor documents in place to use unified carehq actor types.
    """

    def setUp(self):
        from django.contrib.auth.models import User
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


    def testCreateActorInView(self):
        """
        Call view function directly for API testing verification
        """
        from pactcarehq.views.providers import pt_new_or_link_provider

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


