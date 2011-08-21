from casexml.apps.case.models.couch import CommCareCase
from dimagi.utils.couch.database import get_db


def run():
    """
    This method is now deprecated now that migrate2 has been run
    """
    return
    cases = CommCareCase.view('case/by_xform_id', include_docs=True).all()
    print "got cases: %d" % (len(cases))
    db = get_db()
    for case in cases:
        print case
        delresult = db.delete_doc(case)
        print delresult



