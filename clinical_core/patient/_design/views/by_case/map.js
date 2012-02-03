function(doc) {
    //key = doc id
    if (doc.base_type == "BasePatient")
        emit(doc.case_id, null);
}