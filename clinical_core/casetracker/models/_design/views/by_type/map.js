function(doc) {
    if (doc.base_type == "Case")
        emit(doc.doc_type, null);
}