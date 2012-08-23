function (doc) {
    if(doc['doc_type'] == "XFormInstance") {
        if(doc.xmlns == "http://dev.commcarehq.org/pact/progress_note" || doc.xmlns == "http://dev.commcarehq.org/pact/dots_form") {
            //no metas
            if(doc.form.meta === undefined) {
                emit(["nometa", doc.received_on, doc.xmlns], null);
            }
        }
        //no pact ids
        if(doc.xmlns == "http://dev.commcarehq.org/pact/dots_form") {
            if (doc.form.pact_id == "" || doc.form.pact_id === undefined) {
                emit(["no pact id", doc.xmlns, doc.received_on], null);
            }
        }
        if(doc.xmlns == "http://dev.commcarehq.org/pact/progress_note") {
            if (doc.form.note.pact_id == "" || doc.form.note.pact_id === undefined) {
                emit(["no pact id", doc.xmlns, doc.received_on], null);
            }
        }
        if (doc.problem != undefined) {
            emit(["problem", doc.xmlns, doc.received_on], doc.problem);
        }
    }
}