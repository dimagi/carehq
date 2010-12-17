function(doc) { 
    if (doc.doc_type == "CPatient") {
        emit(doc.last_name.toLowerCase() + doc.first_name.toLowerCase() + doc.birthdate, null);
    }
}