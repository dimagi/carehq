from django.test import TestCase
import os
from datetime import datetime, timedelta
from clincore.utils import ms_from_timedelta
from couchforms.signals import xform_saved
from couchforms.util import post_xform_to_couch


class SubmitParsingTests(TestCase):
    def setUp(self):
        pass

    def testSubmitAndVerifyParse(self):
        print "in testSubmitAndVerifyParse"
        sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sampledata')
        files = os.listdir(sample_dir)
        for f in files:
            fin = open(os.path.join(sample_dir, f), 'r')
            xml_string = fin.read()
            fin.close()

            start_time = datetime.utcnow()
            print "Begin sample submission"
            doc = post_xform_to_couch(xml_string)
            delta_post =  datetime.utcnow() - start_time
            print "Submission posted: %d ms" % (ms_from_timedelta(delta_post))
            #xform_saved.send(sender="post", xform=doc) #ghetto way of signalling a submission signal
            #delta_signal = datetime.utcnow() - (start_time + delta_post)
            #print "Signal emitted: %d ms" % (ms_from_timedelta(delta_signal))

            self.assertTrue(isinstance(doc['form']['case']['update']['dots'], dict))


        pass



