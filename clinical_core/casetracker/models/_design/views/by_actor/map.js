function(doc) { 
    if (doc.base_type == "Case")  {
        emit(['assigned_to', doc.assigned_to], doc);
        emit(['opened_by', doc.opened_by], doc);
        emit(['last_edit_by', doc.last_edit_by], doc);
        emit(['resolved_by', doc.resolved_by], doc);
        emit(['closed_by', doc.closed_by], doc);
        emit(['last_event_by', doc.events[doc.events.length-1].created_by], doc);
    }
}