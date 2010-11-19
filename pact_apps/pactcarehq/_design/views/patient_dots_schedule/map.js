function(doc) {
	//patient_docts_schedule
    if (doc.doc_type == "CPatient") {
        emit(doc.pact_id, doc.weekly_schedule);
    }
}