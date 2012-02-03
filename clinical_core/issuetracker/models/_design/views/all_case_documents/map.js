function(doc) {
    //key = doc id
    if (doc.doc_type == "CaseDoc")
        emit(doc._id, null);
}