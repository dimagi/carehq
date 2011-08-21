

def delete_all(couchmodel, view_name, key=None, startkey=None, endkey=None):
    """Helper function to help delete/clear documents from the database of a certain type.
    Will call the view function opon a given couchdbkit model you specify (couchmodel), on the given view.  It will do an include_docs on the view request
    to get the entire document, it must return the actual couchmodel instances for the view for this to work.

    After that, it'll iterate through all the elements to delete the items in the resultset.
    """
    params = {}
    if key != None:
        params['key'] = key
    if startkey != None and endkey != None:
        params['startkey'] = startkey
        params['endkey'] = endkey
    params['include_docs'] = True
    data = couchmodel.view(view_name, **params).all()
    total_rows = len(data)

    for dat in data:
        try:
            dat.delete()
        except:
            pass
    return total_rows
