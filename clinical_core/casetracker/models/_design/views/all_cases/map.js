function(doc) {
    if (doc.base_type == "Case")
        emit(doc._id, doc);
}