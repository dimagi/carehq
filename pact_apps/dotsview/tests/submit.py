from StringIO import StringIO
from django.test import TestCase
import os
from contrib_apps.django_digest.test import Client
from couchforms.models import XFormInstance
from couchforms.signals import xform_saved
import re


class SubmitParsingTests(TestCase):
    def setUp(self):
        pass

    def testSubmitAndVerifyParse(self):
        sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sampledata')
        files = os.listdir(sample_dir)
        client = Client()
        uid_re = re.compile('<uid>(?P<doc_id>\w+)<\/uid>')

        for f in files:

            fin = open(os.path.join(sample_dir, f), 'r')
            body = fin.read()
            fin.close()

            payload = StringIO(body.encode('utf-8'))
            payload.name = f
            doc_id = uid_re.search(body).group('doc_id')

            client.post('/receiver2/', data={'xml_submission_file': payload})
            doc = XFormInstance.get(doc_id)
            xform_saved.send(sender="post", xform=doc) #ghetto way of signalling a submission signal
            #delta_signal = datetime.utcnow() - (start_time + delta_post)
            #print "Signal emitted: %d ms" % (ms_from_timedelta(delta_signal))

            self.assertTrue(isinstance(doc['pact_data']['dots'], dict))
            XFormInstance.get_db().delete_doc(doc._id)
        print "foo"

    def testSubmitAndVerifyParseReceiver(self):
        sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sampledata')
        files = os.listdir(sample_dir)
        client = Client()

        fin = open(os.path.join(sample_dir, 'dots1.xml'))
        body = fin.read()
        fin.close()

        f = StringIO(body.encode('utf-8'))
        f.name = 'dots1.xml'

        client.post('/receiver2/', data={'xml_submission_file': f})
        doc = XFormInstance.get('8da7bc705b0111e0bca3cae4957bd0b3')

        XFormInstance.get_db().delete_doc('8da7bc705b0111e0bca3cae4957bd0b3')

