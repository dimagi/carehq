function(doc) {
    //Template care plan ITEMS
    if (doc.doc_type == "BaseCarePlanItem")
        emit([doc.tenant, doc._id], null);
}