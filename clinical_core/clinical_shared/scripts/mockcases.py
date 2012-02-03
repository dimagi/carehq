from clinical_shared.utils import generator, ms_from_timedelta
from datetime import datetime

def run():
    start = datetime.utcnow()
    for i in range(200):
        if i%10 == 0:
            print i
        generator.mock_issue()
    end = datetime.utcnow()
    print "Duration: %d seconds" % (ms_from_timedelta(end-start)/1000)

