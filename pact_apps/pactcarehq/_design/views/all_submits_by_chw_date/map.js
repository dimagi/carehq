function(doc) {

    // !code util/dateparse.js
    if (doc.doc_type == "XFormInstance" && doc.form.Meta !== undefined) {
        emit(doc.form.Meta.username, null);
    }
}