function(doc) {
    if (doc.doc_type == "XFormInstance" && doc.xmlns == "http://dev.commcarehq.org/pact/dots_form" && doc.form.Meta !== undefined) {
        emit(doc.form.pact_id, [doc._id, doc.form.encounter_date]);
    }
}