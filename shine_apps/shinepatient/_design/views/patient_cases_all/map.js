function(doc){
    //returns cases that are known to be linked with patients.
    if(doc.base_type == "BasePatient" && doc.doc_type == "ShinePatient") {
        for (var i = 0; i < doc['cases'].length; i++) {
            emit(doc['cases'][i], null);
        }
    }
}