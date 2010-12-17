function(doc) { 
    if (doc.base_type == "Case")  {
        emit(['assigned_to', doc.assigned_to], null);
        emit(['opened_by', doc.opened_by], null);
        emit(['last_edit_by', doc.last_edit_by], null);
        emit(['resolved_by', doc.resolved_by], null);
        emit(['closed_by', doc.closed_by], null);
        emit(['last_event_by', doc.events[doc.events.length-1].created_by], null);
    }
}