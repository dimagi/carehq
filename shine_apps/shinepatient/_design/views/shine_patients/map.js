function(doc){
    //returns Patient Documents
    if(doc.base_type == "BasePatient" && doc.doc_type == "ShinePatient") {
        emit(doc._id, null);
    }
}