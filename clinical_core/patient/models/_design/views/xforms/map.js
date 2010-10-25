function(doc) { 
    if (doc["#doc_type"] == "XForm") {
        if (doc.case && doc.case.patient_id) {
            emit(doc.case.patient_id, doc);
        }
    } 
}