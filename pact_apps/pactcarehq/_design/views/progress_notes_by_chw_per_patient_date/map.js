function(doc) {
    //Parse the encounter date string.
    //note, that the dates are in 1 indexed months, so NO additions here.
    function parse_date(date_string) {
        if (!date_string) return new Date(1970,1,1);
        // hat tip: http://stackoverflow.com/questions/2587345/javascript-date-parse
        var parts = date_string.match(/(\d+)/g);
        // new Date(year, month [, date [, hours[, minutes[, seconds[, ms]]]]])
        return new Date(parts[0], parts[1]-1, parts[2]); // months are 0-based
    }

    //this is used for the calendar submits for per chw schedule DOTS visits whether or nto they're keeping with their schedule, hence, only dots forms.
    if (doc.doc_type == "XFormInstance" && doc.xmlns == "http://dev.commcarehq.org/pact/progress_note") {
        var edate = parse_date(doc.form.note.encounter_date);
        //return it in regular months, not zero indexed.
        emit([doc.form.Meta.username, doc.form.note.pact_id, edate.getFullYear(), edate.getMonth()+1, edate.getDate()], null);
    }
}