function(doc) {
    if (doc.doc_type == "XFormInstance" && doc.xmlns == "http://dev.commcarehq.org/pact/progress_note" && doc.form.Meta !== undefined) {
        emit(doc.form.note.pact_id, [doc._id, doc.form.note.encounter_date]);
    }
}