function(doc) {
    //all shine patient case types
    if (doc.doc_type == "CommCareCase" && doc.type == "shine_patient") {
        emit (doc._id, null);
    }
}


