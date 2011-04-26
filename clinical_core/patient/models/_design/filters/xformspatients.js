function(doc) {
    if (doc.doc_type == "CPatient") {
       return true;
    }
    if (doc.doc_type == "XFormInstance") {
        return true;
    }
    if (doc.doc_type == "CObservationAddendum") {
        return true;
    }
    return false;
}