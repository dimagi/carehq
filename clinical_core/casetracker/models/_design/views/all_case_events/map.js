function(doc) {
    // all case events, bust out the case events for a global event view
    if (doc.base_type == "Case") {
    //emit over all the events within the case
        for (var i = 0; i < doc.events.length; i++) {
            emit([doc._id, doc.events[i].event_id], doc.events[i]);
        }
    }
}