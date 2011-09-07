function(doc){
    //return cases
    if(doc.doc_type == "CommCareCase" && doc.type=='shine_patient') {// && case.domain == "foo") { //todo: set domain for this project(s)
        emit(doc._id, null);
    }
}