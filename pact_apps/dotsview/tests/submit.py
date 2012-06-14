from StringIO import StringIO
from datetime import timedelta, datetime
from django.core.urlresolvers import reverse
import pdb
from django.contrib.auth.models import User
from django.core.management import call_command
from django.contrib.webdesign import lorem_ipsum
import random
from django.test import TestCase
from django.test.client import RequestFactory
import os
from casexml.apps.case.models import CommCareCase
from clinical_shared.tests.testcase import CareHQClinicalTestCase
from clinical_shared.utils import generator
from contrib_apps.django_digest.test import Client
from couchforms.models import XFormInstance
from couchforms.signals import xform_saved
import re
from pactpatient.enums import PACT_LANGUAGE_CHOICES, GENDER_CHOICES, PACT_RACE_CHOICES, PACT_HIV_CLINIC_CHOICES
from pactpatient.models import PactPatient
from pactpatient.views import new_patient
from patient.models import Patient
from django.contrib.sessions.backends.file import SessionStore
from permissions.models import PrincipalRoleRelation, Role, Actor
from tenant.models import Tenant


REGIMEN_CHOICES = [
    ('morning', 'Morning'),
    ('noon', 'Noon'),
    ('evening', 'Evening'),
    ('bedtime', 'Bedtime'),
    ('morning,noon', 'Morning, Noon'),
    ('morning,evening', 'Morning, Evening'),
    ('morning,bedtime', 'Morning, Bedtime'),
    ('noon,evening', 'Noon, Evening'),
    ('noon,bedtime', 'Noon, Bedtime'),
    ('evening,bedtime', 'Evening, Bedtime'),
    ('morning,noon,evening', 'Morning, Noon, Evening'),
    ('morning,noon,bedtime', 'Morning, Noon, Bedtime'),
    ('morning,evening,bedtime', 'Morning, Evening, Bedtime'),
    ('noon,evening,bedtime', 'Noon, Evening, Bedtime'),
    ('morning,noon,evening,bedtime', 'Morning, Noon, Evening, Bedtime'),
    ]

class DOTSubmitParsingTests(CareHQClinicalTestCase):
    def setUp(self):
        print "setUp!!!"
        User.objects.all().delete()
        Actor.objects.all().delete()
        Role.objects.all().delete()
        Tenant.objects.all().delete()
        Patient.objects.all().delete()
        PrincipalRoleRelation.objects.all().delete()
        call_command('carehq_init')
        self.tenant = Tenant.objects.all()[0]
        self._createUser()
        self.client = Client()

    def testCreatePatientView(self):
        """
        Create a patient via the view.
        """
        #first create some providers
        print "testCreatePatientView"
        chws = []
        for x in range(0,5):
            chws.append(self._new_chw(self.tenant, generator.get_or_create_user()))

        start_pt_count = len(Patient.objects.all())
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
            u'art_regimen': random.choice(REGIMEN_CHOICES)[0],
            u'birthdate': generator.random_past_date().strftime("%m/%d/%Y"),
            u'pact_id': pact_id,
            u'race': random.choice(PACT_RACE_CHOICES)[0],
            u'hiv_care_clinic': random.choice(PACT_HIV_CLINIC_CHOICES)[0],
            u'primary_hp': random.choice(chws).django_actor.user.username,
            u'non_art_regimen': random.choice(REGIMEN_CHOICES)[0],
            u'arm': random.choice(['HP1','HP2','HP3','DOT3','DOT5','DOT7','DOT1']),
            }

        rf = RequestFactory()
        login_resp = self.client.post('/accounts/login/', {'username': 'mockmock@mockmock.com', 'password': 'mockmock'})
        resp = self.client.post(reverse('new_pactpatient'), data = newpatient_data)
        fout = open('foo.html','w')
        fout.write(resp.content)
        fout.close()
        self.assertEquals(Patient.objects.all().count(), start_pt_count+1)

        pt_case_doc_view = PactPatient.view('pactcarehq/patient_pact_ids', key=pact_id, include_docs=True).all()
        self.assertEquals(len(pt_case_doc_view), 1)
        pt_case_doc = pt_case_doc_view[0]
        self.assertTrue(CommCareCase.get_db().doc_exist(pt_case_doc.case_id))
        return pt_case_doc

    def testSubmitAndVerifyParse(self):
        print "testSubmitAndVerifyParse"
        patient_doc = self.testCreatePatientView()

        sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sampledata')
        files = os.listdir(sample_dir)
        uid_re = re.compile('<uid>(?P<doc_id>\w+)<\/uid>')

        for f in files:
            print "submitting file: %s" % f
            fin = open(os.path.join(sample_dir, f), 'r')
            body = fin.read()
            fin.close()
            body = body % {'case_id':patient_doc.case_id}
            body = body.replace('\n','')

            payload = StringIO(body)
            payload.name = f
            doc_id = uid_re.search(body).group('doc_id')

            self.client.post('/receiver/submit', data={'xml_submission_file': payload})
            doc = XFormInstance.get(doc_id)
            xform_saved.send(sender="post", xform=doc) #ghetto way of signalling a submission signal
            #delta_signal = datetime.utcnow() - (start_time + delta_post)
            #print "Signal emitted: %d ms" % (ms_from_timedelta(delta_signal))

            self.assertTrue(isinstance(doc['pact_data']['dots'], dict))
            XFormInstance.get_db().delete_doc(doc._id)

    def testSubmitAndVerifyParseReceiver(self):
        sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sampledata')
        files = os.listdir(sample_dir)

        fin = open(os.path.join(sample_dir, 'dots1.xml'))
        body = fin.read()
        fin.close()

        f = StringIO(body.encode('utf-8'))
        f.name = 'dots1.xml'

        self.client.post('/receiver/submit', data={'xml_submission_file': f})
        doc = XFormInstance.get('8da7bc705b0111e0bca3cae4957bd0b3')

        XFormInstance.get_db().delete_doc('8da7bc705b0111e0bca3cae4957bd0b3')

