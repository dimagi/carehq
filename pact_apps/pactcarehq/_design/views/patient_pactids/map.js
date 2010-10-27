function(doc) {
    if (doc.doc_type == "CPatient") {
        emit(doc.pact_id, doc);
    }
}