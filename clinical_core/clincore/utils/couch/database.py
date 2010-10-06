
def get_db():
    """
    Get the bhoma database.  
    """
    # this is a bit of a hack, since it assumes all the models talk to the same
    # db.  that said a lot of our code relies on that assumption.
    # this import is here because of annoying dependencies
    from bhoma.apps.patient.models import CPatient
    return CPatient.get_db()

def get_view_names(database):
    design_docs = database.view("_all_docs", startkey="_design/", 
                                endkey="_design/zzzz")
    views = []
    for row in design_docs:
        doc_id = row["id"]
        doc = database.get(doc_id)
        doc_name = doc_id.replace("_design/", "")
        if "views" in doc:
            for view_name, _ in doc["views"].items(): 
                views.append("%s/%s" % (doc_name, view_name))
    return views