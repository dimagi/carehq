function(doc) {
    if (doc.doc_type == "XFormInstance" && doc.xmlns == "http://dev.commcarehq.org/pact/progress_note" && doc.form.Meta !== undefined) {
        emit(doc.form.Meta.username, doc);
    }
}