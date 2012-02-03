from StringIO import StringIO
import codecs
import hashlib
import pdb
from BeautifulSoup import BeautifulStoneSoup
from couchdbkit.consumer import Consumer
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
import os
from couchforms.models import XFormInstance
from receiver.util import spoof_submission

class ccdSignalTest(TestCase):

    def setUp(self):
        file_root = os.path.abspath(os.path.dirname(__file__))
        self.examples_dir = os.path.join(file_root, 'testfiles')
        self.client = Client()

        self.db = XFormInstance.get_db()
        self.consumer = Consumer(self.db)

    def get_files(self):
        for filename in os.listdir(self.examples_dir):
            yield codecs.open(os.path.join(self.examples_dir, filename), encoding='utf-8', mode='r')


    def testSubmitCCD(self):
        for ccd_filestream in self.get_files():
            ccd_to_test = ccd_filestream.read()
            ccd_stream = StringIO(ccd_to_test.encode('utf-8'))
            ccd_stream.name='form.xml'
            start_seq=self.consumer.fetch()['last_seq']

            resp = self.client.post(reverse('carehqapp.views.ccdreceiver.receive_ccd'), { 'patientsessiondata': ccd_stream })

#            resp = spoof_submission(reverse('carehqapp.views.ccdreceiver.receive_ccd'), ccd_to_test, hqsubmission=False)

            content = resp.content

            #Parse the response from the POST
            soup = BeautifulStoneSoup(content)
            self.assertEquals(soup.code.text,"SUCCESS")
            response_id = soup.message.text.split(':')[-1].strip()

            #get the changes feed to see the new doc just created
            end_seq = self.consumer.fetch(since=start_seq)['last_seq']
            self.assertEquals(start_seq+1, end_seq)
            end_changes_doc_id = self.consumer.fetch(since=start_seq)['results'][0]['id']

            #verify that the changes feed and the id returned from the response xml match
            self.assertEqual(end_changes_doc_id, response_id)

            #get the db document and verify the attachment is there
            doc = self.db.get(response_id)
            attachment = self.db.fetch_attachment(response_id, 'form.xml').encode('utf-8')


            #verify checksum matches of submitted with what's retrieved.
            self.assertEquals(hashlib.md5(attachment).hexdigest(), hashlib.md5(ccd_to_test.encode('utf-8')).hexdigest())






