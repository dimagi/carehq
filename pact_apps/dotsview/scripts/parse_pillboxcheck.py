from couchforms.models import XFormInstance
import simplejson

def run():
    docs = XFormInstance.view('pactcarehq/all_dots_forms', include_docs=True).all()
    for doc in docs:
        try:
            if isinstance(doc['form']['pillbox_check'], str):
                continue

            if isinstance(doc['form']['pillbox_check'], unicode):
                continue

            if not doc['form']['pillbox_check'].has_key('check'):
                print "don't got check key"
                continue

            pillbox_check_str = doc['form']['pillbox_check']['check']
            if isinstance(pillbox_check_str, dict):
                #print "dictionary, skipping"
                continue
            elif isinstance(pillbox_check_str, str) or isinstance(pillbox_check_str, unicode):
                json_data = simplejson.loads(pillbox_check_str)
                print "parsing string json"
                doc['form']['pillbox_check']['check'] = json_data


                str1 = simplejson.dumps(json_data)
                str2 = simplejson.dumps(doc['form']['case']['update']['dots'])
                if str1 == str2:
                    print "Values are equal"
                doc.save()
        except Exception, ex:
            print "Error - dots key not present: version %s uiVersion %s" % (doc['form']['@version'], doc['form']['@uiVersion'])
            print "Doc in question: %s" % (doc._id)
            print doc['form']['pillbox_check']['check']
            print "Exception: %s" % (ex.message)

