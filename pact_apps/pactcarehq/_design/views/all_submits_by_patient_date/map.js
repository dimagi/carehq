function(doc) {
    if (doc.doc_type == "XFormInstance") {
        emit([doc.form.pact_id, parseInt(doc.form.encounter_date.substring(0,4)), parseInt(doc.form.encounter_date.substring(5,7))+1, parseInt(doc.form.encounter_date.substring(8,10)), doc.xmlns], doc);
    }
}