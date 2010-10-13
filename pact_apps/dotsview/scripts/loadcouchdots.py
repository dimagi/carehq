from couchforms.models import XFormInstance
from dotsview.formprocess import process_dots_json

def run():
    docs = XFormInstance.view('pactcarehq/all_dots_forms').all()


    for doc in docs:
        try:
            dots_json = doc['form']['case']['update']['dots']
            observations = process_dots_json(doc, dots_json)
        except Exception, ex:
            print "Error - dots key not present: version %s uiVersion %s" % (doc['form']['@version'], doc['form']['@uiVersion'])
            print "Exception: %s" % (ex.message)

