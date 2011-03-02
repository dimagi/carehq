function(doc) {
    function make_date_key(dateproperty, datestring, doc) {
        if (datestring == null) {
            //if it's null don't bother emitting
            return;
        }
        var dateval = new Date(Date.parse(datestring));
        emit([dateproperty,
            dateval.getFullYear(),
            dateval.getMonth()+1, //months are zero indexed, damn it
            dateval.getDate(),
            dateval.getHours(),
            dateval.getMinutes(),
            dateval.getSeconds(),
            dateval.getMilliseconds()], null);
    }


    if (doc.base_type == "Case")  {
        make_date_key('assigned_date', doc.assigned_date, doc);
        make_date_key('opened_date', doc.opened_date, doc);
        make_date_key('last_edit_date', doc.last_edit_date, doc);
        make_date_key('resolved_date', doc.resolved_date, doc);
        make_date_key('due_date', doc.due_date, doc);
        make_date_key('closed_date', doc.closed_date, doc);
        make_date_key('last_event_date', doc.events[doc.events.length-1].created_date, doc);
    }
}