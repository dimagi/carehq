function(doc) { 
    if (doc.doc_type == "CPatient" && doc.arm == "DOT")
        emit(doc._id, doc); 
}