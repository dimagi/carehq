from actorpermission.models import *
from django.core.management import call_command
import simplejson
from StringIO import StringIO

def run():
    patients=Patient.objects.all()


    print "outputting raw cases"
    with open('pact_raw_cases.json', 'wb') as fout:
        output_json = []
        for pt in patients:
            patient_doc = getattr(pt, 'couchdoc', None)
            if patient_doc is not None:
                case_doc = patient_doc.get_case()
                output_json.append(case_doc)
        fout.write(simplejson.dumps(output_json))

    print "raw case export finished"
