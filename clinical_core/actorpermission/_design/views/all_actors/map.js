function(doc) {
    //key = doc id
    if (doc.base_type == "BaseActorDocument")
        emit(doc._id, null);
}