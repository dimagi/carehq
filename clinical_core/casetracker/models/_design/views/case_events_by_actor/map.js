function(doc) {
    // all case events, by the created_by
    if (doc.base_type == "Case") {
    //emit over all the events within the case
        for (var i = 0; i < doc.events.length; i++) {
            emit(doc.events[i].created_by, doc.events[i]);
        }
    }
}