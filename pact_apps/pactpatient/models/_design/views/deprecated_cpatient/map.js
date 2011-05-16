function(doc) {
    //if it has a doctype of cpatient, in this codebase, then that means we need to migrate it over.
    if (doc.doc_type == "CPatient")
        emit(doc._id, null);
}