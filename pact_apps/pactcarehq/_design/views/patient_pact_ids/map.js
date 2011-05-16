function(doc) {
    //key = pact_id
    if (doc.base_type == "BasePatient")
        emit(doc.pact_id, null);
}