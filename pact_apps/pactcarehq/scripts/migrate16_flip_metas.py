from couchforms.models import XFormInstance
from receiver.signal_emits import scrub_meta
import thread


NUM_THREADS = 1


#source http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
def chunks(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]


def do_operation(xform_ids, counter):
    print "Starting ids: %d" % counter
    print "ids: #%s#" % xform_ids
    for id in xform_ids:
        try:
            xform = XFormInstance.get(id)
            print "\tScrubbed (%d) %s" % (counter, id)
            scrub_meta(None, xform)
        except Exception, ex:
            print "%d: %s %s" % (counter, id, ex)
    print "finish %d" % counter



def run():
    #convert patient from pact_id 493 to 199 due to a clerical/data entry accounting error. This should not be done
    #in other circumstances.

    namespaces = [
        #"http://code.javarosa.org/devicereport",
        #"http://dev.commcarehq.org/CCPTZ/ccptz_encounter",
        "http://dev.commcarehq.org/pact/bloodwork",
        "http://dev.commcarehq.org/pact/dots_form",
        "http://dev.commcarehq.org/pact/mileage",
        "http://dev.commcarehq.org/pact/patientupdate",
        "http://dev.commcarehq.org/pact/progress_note",
        "http://openrosa.org/app/general",
        "https://www.commcarehq.org/test/casexml-wrapper",
        ]

    threadcount = 0
    for xmlns in namespaces:
        print "Processing xmlns %s" % xmlns
        xform_vals = XFormInstance.view('couchforms/by_xmlns', key=xmlns, reduce=False).all()
        xform_ids = [x['id'] for x in xform_vals]

        slice_size = len(xform_ids) / NUM_THREADS

        if NUM_THREADS == 1:
            do_operation(xform_ids, 1)
        else:
            if slice_size == 0:
                slices = xform_ids
            else:
                slices = chunks(xform_ids, slice_size)

            try:
                for slice in slices:
                    thread.start_new_thread( do_operation, (slice, threadcount))
                    threadcount += 1
            except:
                print "unable to start thread"








