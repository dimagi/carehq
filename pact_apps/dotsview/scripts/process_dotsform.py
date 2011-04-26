from couchforms.models import XFormInstance
from dotsview.formprocess import process_dots_json
import simplejson
import hashlib

def run():

    offset = 0
    block_size = 250

    while True:
        docs = XFormInstance.view('pactcarehq/all_dots_forms', include_docs=True, skip=offset, limit=block_size).all()
        if len(docs) == 0:
            break
        for xform in docs:
            try:
                if isinstance(xform['form']['case']['update'], str):
                    continue

                if isinstance(xform['form']['case']['update'], unicode):
                    continue

                if not xform['form']['case']['update'].has_key('dots'):
                    continue

                dots_json = xform['form']['case']['update']['dots']
                if isinstance(dots_json, dict):
                    print "reprocessing dots json from json back to original string"
                    #it's a dictionary, put the dictionary on a pact_property
                    xform['pact_data'] = {}
                    xform['pact_data']['dots'] = dots_json
                    #reset the case block to be a string
                    xform['form']['case']['update']['dots'] = simplejson.dumps(dots_json)
                    xform.save()
                elif isinstance(dots_json, str) or isinstance(dots_json, unicode):
                    if not hasattr(xform, 'pact_data'):
                        print "Unprocessed form, setting pact_data: %s" % (xform._id)
                        dots_json_str = xform['form']['case']['update']['dots']
                        json_data = simplejson.loads(dots_json_str)
                        xform['pact_data'] = {}
                        xform['pact_data']['dots'] = json_data
                        xform.save()
                    else:
                        print "has pact_data: %s" % (xform['pact_data'])
            except Exception, ex:
                print "Error - dots key not present: version %s uiVersion %s" % (xform['form']['@version'], xform['form']['@uiVersion'])
                print "Doc in question: (%s): %s->%s" % (xform._id, xform, dir(xform))
                print "Exception: %s" % (ex.message)
        offset += block_size

