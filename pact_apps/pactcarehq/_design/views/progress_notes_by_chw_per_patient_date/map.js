function(doc) {
    //Parse the encounter date string.
    //note, that the dates are in 1 indexed months, so NO additions here.
    // !code util/dateparse.js

    //this is used for the calendar submits for per chw schedule DOTS visits whether or nto they're keeping with their schedule, hence, only dots forms.
    if (doc.doc_type == "XFormInstance" && doc.xmlns == "http://dev.commcarehq.org/pact/progress_note") {
        var edate = parse_date(doc.form.note.encounter_date);
        //return it in regular months, not zero indexed.
        emit([doc.form.meta.username, doc.form.note.pact_id, edate.getFullYear(), edate.getMonth()+1, edate.getDate()], null);
    }
}