function(doc) { 
    if (doc.base_type == "Case" && doc.parent_case != null) 
        emit(doc.parent_case, doc._id); 
}