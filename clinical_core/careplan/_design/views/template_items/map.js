function(doc) {
    //Template care plan ITEMS
    if (doc.doc_type == "BaseCarePlanItem")
        emit(doc._id, null);
}