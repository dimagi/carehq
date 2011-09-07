function(doc){
    if(doc.base_type == "BasePatient" && doc.doc_type == "ShinePatient") {
        for (var i = 0; i < doc['cases'].length; i++) {
            emit(doc['cases'][i], null);
        }
    }
}