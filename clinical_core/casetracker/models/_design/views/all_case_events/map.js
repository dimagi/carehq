function(doc) {
    // all case events, bust out the case events for a global event view
    if (doc.base_type == "Case") {
    //emit over all the events within the case
        for (var i = 0; i < doc.events.length; i++) {
            var dateval = new Date(Date.parse(doc.events[i].created_date));
            emit([doc._id,
                dateval.getFullYear(),
                dateval.getMonth()+1, //months are zero indexed, damn it
                dateval.getDate(),
                dateval.getHours(),
                dateval.getMinutes(),
                dateval.getSeconds(),
                dateval.getMilliseconds()
                ], doc.events[i]);
        }
    }
}