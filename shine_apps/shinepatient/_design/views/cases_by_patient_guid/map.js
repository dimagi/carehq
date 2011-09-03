function(doc){
    if(doc.doc_type == "CommCareCase") {// && case.domain == "foo") { //todo: set domain for this project(s)
        emit(doc.patient_guid, null);
    }
}