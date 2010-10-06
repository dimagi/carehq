function(doc) { 
    if (doc.doc_type == "CPatient") 
        emit(doc._id, null); 
}