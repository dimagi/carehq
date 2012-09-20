from patient.models import Patient

def run():

    """
    Loop through all the regimens for patients and spoof submit the old regimens to new (default) labeled ones and update the caseblock accordingly
    """
    from casexml.apps.case.models import CommCareCase
    patients = Patient.objects.all()
    for pt in patients:
        case_id = pt.couchdoc.case_id
        print "Updating Case ID: %s" % case_id
        casedoc = CommCareCase.get(case_id)

        is_changed = False
        if hasattr(casedoc, 'artregimen') and casedoc.artregimen == '0':
            casedoc.artregimen = ''
            is_changed = True
        if hasattr(casedoc, 'nonartregimen') and casedoc.nonartregimen == '0':
            casedoc.nonartregimen = ''
            is_changed = True

        if is_changed:
            print "\tchanging regimens for %s" % case_id
            casedoc.save()

