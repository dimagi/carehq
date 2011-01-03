function(doc) {
	if (doc.doc_type == "CPatient") {
        emit(doc.primary_hp, doc.pact_id);
	}
}