from couchforms.models import XFormInstance
from dotsview.formprocess import process_dots_json
import simplejson
import hashlib


#does various hashes on an xform instance to provide some quick reports on dupes and other similar data.

def run():
    docs = XFormInstance.view('pactcarehq/all_dots_forms').all()
    for doc in docs:
        form = doc.form
        json = doc.to_json()
        try:
            form = json['form']
            strjson = str(json)
            form_md5 = hashlib.md5(strjson).hexdigest()
            xml_md5 = doc.xml_md5()
            doc.attachment_md5 = xml_md5
            doc.form_md5 = form_md5
        
            casejson = str(json['form']['case']['update'])
            case_md5 = hashlib.md5(casejson).hexdigest()
            doc.case_md5 = case_md5
            doc.save()
        except:
            print "no update"
    print "done"
        
