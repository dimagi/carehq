function(doc) { 
    if (doc.base_type == "BasePatient") {
        emit(doc.last_name.toLowerCase(), null);
    }
}