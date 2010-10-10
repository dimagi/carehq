function(doc) { 
    if (doc.doc_type == "CPatient") {
        emit(doc.last_name.toLowerCase() + "_" + doc.first_name.toLowerCase(), doc);
    }
}