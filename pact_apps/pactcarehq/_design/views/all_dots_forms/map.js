function(doc) {
    if (doc.doc_type == "XFormInstance" && doc.xmlns == "http://dev.commcarehq.org/pact/dots_form" && doc.form.Meta !== undefined) {
        emit([doc.form.Meta.username, doc.form.pact_id], null);
    }
}