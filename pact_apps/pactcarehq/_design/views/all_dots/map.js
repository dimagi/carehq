function(doc) {
    //view to see all patients that are DOT patients.
    if (doc.base_type == "BasePatient" && doc.arm == "DOT")
        emit(doc._id, null); 
}