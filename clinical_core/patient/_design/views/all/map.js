function(doc) {
    //key = doc id
    if (doc.base_type == "BasePatient")
        emit(doc._id, null); 
}