from couchforms.models import XFormInstance
from dotsview.formprocess import process_dots_json
import simplejson
import hashlib

def run():
    docs = XFormInstance.view('pactcarehq/all_dots_forms').all()
    for doc in docs:
        try:
            if not doc['form']['case']['update'].has_key('dots'):
                print "don't got dots key"
                continue

            dots_json = doc['form']['case']['update']['dots']
            if isinstance(dots_json, dict):
                print "dictionary, skipping"
                continue
            elif isinstance(dots_json, str):
                json_data = simplejson.loads(dots_json)
                print "parsing string json"
                doc['form']['case']['update']['dots'] = json_data
                doc.save()
        except Exception, ex:
            print "Error - dots key not present: version %s uiVersion %s" % (doc['form']['@version'], doc['form']['@uiVersion'])
            print "Exception: %s" % (ex.message)

