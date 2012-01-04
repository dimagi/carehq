import hashlib
import pdb
from BeautifulSoup import BeautifulStoneSoup
from couchdbkit.consumer import Consumer
from django.core.urlresolvers import reverse
from django.test import TestCase
import os
from couchforms.models import XFormInstance
from receiver.util import spoof_submission

class ccdSubmitTest(TestCase):

    def setUp(self):
        filepath = os.path.abspath(os.path.dirname(__file__))
        fin1 = open(os.path.join(filepath, 'CCD03.xml'),'r')
        self.ccd_one = fin1.read()
        fin1.close()

        fin2 = open(os.path.join(filepath, 'CCD04.xml'),'r')
        self.ccd_two = fin2.read()
        fin2.close()

        self.db = XFormInstance.get_db()
        self.consumer = Consumer(self.db)

    def testSubmitCCD(self):

        for ccd_to_test in [self.ccd_one, self.ccd_two]:
            start_seq=self.consumer.fetch()['last_seq']
            resp = spoof_submission(reverse('carehqapp.views.ccdreceiver.receive_ccd'), ccd_to_test, hqsubmission=False)
            content = resp.content
            soup = BeautifulStoneSoup(content)

            self.assertEquals(soup.code.text,"SUCCESS")

            response_id = soup.message.text.split(':')[-1].strip()

            end_seq = self.consumer.fetch(since=start_seq)['last_seq']
            self.assertEquals(start_seq+1, end_seq)

            end_changes_doc_id = self.consumer.fetch(since=start_seq)['results'][0]['id']

            self.assertEqual(end_changes_doc_id, response_id)

            doc = self.db.get(response_id)
            attachment = self.db.fetch_attachment(response_id, 'form.xml')

            self.assertEquals(hashlib.md5(attachment.replace('\r','')).hexdigest(), hashlib.md5(ccd_to_test.replace('\r','')).hexdigest())





