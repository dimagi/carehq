from pactcarehq.models import trial1mapping

def run():
    trs = trial1mapping.objects.all()
    ids = []
    for tr in trs:
        ids.append(tr.get_new_patient_doc_id())
    print ids