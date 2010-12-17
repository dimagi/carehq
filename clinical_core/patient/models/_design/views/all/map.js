function(doc) {
    //key = doc id
    if (doc.doc_type == "CPatient") 
        emit(doc._id, null); 
}