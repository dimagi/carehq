function(doc) {
    if (doc.base_type == "BasePatient") {
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