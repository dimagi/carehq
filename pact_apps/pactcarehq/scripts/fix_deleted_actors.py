from actorpermission.models import CHWActor
from permissions.models import Actor

def run():
    actors = Actor.objects.all()
    db = CHWActor.get_db()

    for a in actors:
        doc_id = a.doc_id
        doc = db.open_doc(doc_id)
        if doc['base_type'].startswith('Deleted'):
            doc['base_type'] = doc['base_type'].replace('Deleted','')
            print "fixing deleted base_type"

        if doc['doc_type'].startswith('Deleted'):
            doc['doc_type'] = doc['doc_type'].replace('Deleted','')
            print "fixing deleted doc_type"
        db.save_doc(doc)



