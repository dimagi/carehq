function(doc) {
    if (doc.doc_type == "Case")
        emit(doc._id, doc);
}