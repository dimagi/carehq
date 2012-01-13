function(doc) {
    // Care Plan Instances by patient
    if (doc.doc_type == "CarePlanInstance")
        emit(doc.patient_guid, null);
}