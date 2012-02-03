function(doc) {
    //Care Plan Instances by ID
    if (doc.doc_type == "CarePlanInstance")
        emit(doc._id, null);
}