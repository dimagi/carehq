from pactpatient.models import PactPatient

def run():
    #really hacky script to address null issues in couch for patient data.  a weird issue not able to pinpoint.
    #patients = PactPatient.view('patient/all').all()
    db = PactPatient.get_db()
    rawdocs = db.view('patient/all' ).all()
    for doc in rawdocs:
        #print doc
        try:
            ptdoc = doc['value']
            phone_hash = ptdoc['phones']
            for ph in phone_hash:
                print ph
                print ph.keys()
                ph['is_default'] = False
            pt = PactPatient.wrap(ptdoc)
            for phone in pt.phones:
                #print phone.is_default
                phone.save()
            pt.save()
        except Exception, e:

            print ptdoc
            print e
            print "fail!"

    #get_db().view('patient/all')
    #for pt in patients:
        #print pt
