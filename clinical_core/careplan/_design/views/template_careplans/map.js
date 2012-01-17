function(doc) {
    //This is for template grouped care plans
    if (doc.doc_type == "BaseCarePlan")
        emit([doc.tenant, doc._id], null);
}