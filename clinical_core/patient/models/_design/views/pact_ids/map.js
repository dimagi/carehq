function(doc) {
    //key = pact_id
    if (doc.doc_type == "CPatient") 
        emit(doc.pact_id, doc);
}