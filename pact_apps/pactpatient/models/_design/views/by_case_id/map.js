function(doc) {
    //emit the patient's case_id where casexml is used for OTA restore on patient longitudinal information
    if (doc.doc_type == "PactPatient")
        emit(doc.case_id, null);
}