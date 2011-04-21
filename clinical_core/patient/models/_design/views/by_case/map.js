function(doc) {
    //key = doc id
    if (doc.doc_type == "CPatient") 
        emit(doc.case_id, null);
}