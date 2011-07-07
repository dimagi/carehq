function(doc){
    if(doc.doc_type == "CommCareCase" && doc.patient_guid) {
        emit(doc.patient_guid, null);
    }
}