function(doc) {
	//patient_pactids
    if (doc.doc_type == "CPatient") {
        emit(doc.pact_id, null);
    }
}