function(doc) {
    if (doc.doc_type == "XFormInstance" && doc.form.Meta !== undefined) {
        emit(doc.form.Meta.username, doc);
    }
}