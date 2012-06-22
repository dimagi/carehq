import pdb
import random
import uuid
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.test.client import Client
from actorpermission.models import CHWActor, ProviderActor, CaregiverActor
from carehq_core import carehq_api
from casexml.apps.case.models import CommCareCase
from clinical_shared.tests.testcase import CareHQClinicalTestCase
from clinical_shared.utils import generator
from clinical_shared.utils.scrambler import raddress
from pactpatient.enums import REGIMEN_CHOICES, PACT_RACE_CHOICES, PACT_HIV_CLINIC_CHOICES, GENDER_CHOICES, PACT_ARM_CHOICES, PACT_LANGUAGE_CHOICES
from pactpatient.models import PactPatient
from pactpatient.views import new_patient
from patient.models import Patient
from permissions.models import Actor, Role, PrincipalRoleRelation
from permissions.tests import RequestFactory
from tenant.models import Tenant
from django.contrib.sessions.backends.file import SessionStore
from django.test import TestCase

class patientEditTests(CareHQClinicalTestCase):
    """
    Upgrade old style pact Actor documents in place to use unified carehq actor types.
    """

    def setUp(self):
        User.objects.all().delete()
        Actor.objects.all().delete()
        Role.objects.all().delete()
        Tenant.objects.all().delete()
        Patient.objects.all().delete()
        PrincipalRoleRelation.objects.all().delete()
        call_command('carehq_init')
        self.tenant = Tenant.objects.all()[0]
        self._createUser()

    def _new_provider_oldstyle(self, tenant, first_name, last_name):
        #django_actor.name = '%s-%s-%s_%s' % (tenant.prefix, self.__class__.__name__, self.first_name, self.last_name)
        actor = Actor()
        old_class = 'ProviderActor'
        actor.name = '%s-%s-%s_%s' % (tenant.prefix, old_class, first_name, last_name)
        actor.save()
        return actor

    def testCreatePatientView(self):
        """
        Create a patient via the view.
        """
        #first create some providers
        chws = []
        for x in range(0,5):
            chws.append(self._new_chw(self.tenant, generator.get_or_create_user()))


        start_pt_count = Patient.objects.all().count()
        pact_id = generator.random_number(length=9)
        newpatient_data = {
           u'mass_health_expiration': generator.random_future_date().strftime("%m/%d/%Y"),
           u'first_name': generator.random_word(),
           u'last_name': generator.random_word(),
           u'middle_name': generator.random_word(),
           u'preferred_language': random.choice(PACT_LANGUAGE_CHOICES)[0],
           u'ssn': generator.random_word(length=9),
           u'gender': random.choice(GENDER_CHOICES)[0],
           u'notes': generator.random_text(length=160),
           u'art_regimen': random.choice(REGIMEN_CHOICES)[1][0],
           u'birthdate': generator.random_past_date().strftime("%m/%d/%Y"),
           u'pact_id': pact_id,
           u'race': random.choice(PACT_RACE_CHOICES)[0],
           u'hiv_care_clinic': random.choice(PACT_HIV_CLINIC_CHOICES)[0],
           u'primary_hp': random.choice(chws).django_actor.user.username,
           u'non_art_regimen': random.choice(REGIMEN_CHOICES)[1][0],
           u'hp_status': random.choice(['HP1','HP2','HP3','']),
           u'dot_status': random.choice(['', 'DOT3','DOT5','DOT7','DOT1']),
        }

        rf = RequestFactory()
        request = rf.get('/')
        request.session = SessionStore()
        request.user = self.user
        request.POST = newpatient_data
        request.method = "POST"
        resp = new_patient(request)
        fout = open('foo.html','w')
        fout.write(resp.content)
        fout.close()

        self.assertEquals(Patient.objects.all().count(), start_pt_count+1)

        pt_case_doc_view = PactPatient.view('pactcarehq/patient_pact_ids', key=pact_id, include_docs=True).all()
        self.assertEquals(len(pt_case_doc_view), 1)
        pt_case_doc = pt_case_doc_view[0]

        self.assertTrue(CommCareCase.get_db().doc_exist(pt_case_doc.case_id))

    def testCreateActorInView(self):
        """
        Call view function directly for API testing verification
        """
        from pactcarehq.views.providers import pt_new_or_link_provider
        start_prr = int(PrincipalRoleRelation.objects.count())
        user = generator.generate_random_user()
        patient = generator.get_or_create_patient(self.tenant, user=None, first_name="Jean-luc", last_name="Picard")
        form_data = {'phone_number': u'6171234567', 'first_name': u'Gregory', 'last_name': u'House',
                     'title': u'Dr.', 'facility_name': u'Princeton General', 'notes': u'Mock Made',
                     'provider_title': u'Diagnostician',
                     'facility_address': u'erdfb3245', 'email': u'cxvbxvcb'}

        rf = RequestFactory()
        request = rf.get('/')
        request.session = SessionStore()
        request.user = user
        request.POST = form_data
        request.method = "POST"
        resp = pt_new_or_link_provider(request, patient._id)

        end_prr = PrincipalRoleRelation.objects.count()
        self.assertEqual(start_prr + 2, end_prr)

        local_prrs = PrincipalRoleRelation.objects.filter(content_type=ContentType.objects.get_for_model(Patient))
        self.assertEqual(local_prrs.count(), 1)

        general_prrs = PrincipalRoleRelation.objects.filter(content_type=None)
        self.assertEqual(general_prrs.count(), 1)

