function(doc) {
    if (doc.doc_type == "CommCareCase") {
        emit(doc.form.pact_id, [doc._id, doc.form.encounter_date]);
    }
}