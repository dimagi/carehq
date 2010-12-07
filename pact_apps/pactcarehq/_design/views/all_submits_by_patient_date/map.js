function(doc) {
    //Parse the encounter date string.
    //note, that the dates are in 1 indexed months, so NO additions here.
    if (doc.doc_type == "XFormInstance") {
        emit([doc.form.pact_id, parseInt(doc.form.encounter_date.substring(0,4)), parseInt(doc.form.encounter_date.substring(5,7)), parseInt(doc.form.encounter_date.substring(8,10)), doc.xmlns], doc);
    }
}