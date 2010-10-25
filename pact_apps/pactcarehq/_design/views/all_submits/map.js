function(doc) {
    if (doc.doc_type == "XFormInstance") {
        emit(doc.form.Meta.username, doc);
    }
}