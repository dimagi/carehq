function(doc) {
    if (doc.base_type == "ProfileDocument") {
        emit(doc._id, null);
    }
}