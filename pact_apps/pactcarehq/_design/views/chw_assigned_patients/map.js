function(doc) {
	if (doc.base_type == "BasePatient") {
        emit(doc.primary_hp, doc.pact_id);
	}
}