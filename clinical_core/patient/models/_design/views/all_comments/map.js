function(doc) {
    if (doc.doc_type == "CSimpleComment") {
        emit(doc.doc_fk_id, doc);
    }
}