function(doc) { 
    if (doc.doc_type == "CPatient") {
        emit(doc.last_name.toLowerCase(), doc);
    }
}