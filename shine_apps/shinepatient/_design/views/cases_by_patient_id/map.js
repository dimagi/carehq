function(doc){
    if(doc.doc_type == "CommCareCase" && doc.patient_id) {
        emit(doc.patient_id, null);
    }
}