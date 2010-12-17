function(doc) { 
    if (doc.base_type == "Case") 
        emit(doc.patient, null); 
}