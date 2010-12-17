function(doc) {
    //Parse the encounter date string.
    //note, that the dates are in 1 indexed months, so NO additions here.
    if (doc.doc_type == "XFormInstance") {
        emit(doc.form.pact_id, null);
    }
}