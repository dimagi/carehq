function(doc) {
    //all submissions for DOTS notes by date
    //Parse the encounter date string.
    //note, that the dates are in 1 indexed months, so NO additions here.
    function parse_date(date_string) {
        if (!date_string) return new Date(1970, 1, 1);
        // hat tip: http://stackoverflow.com/questions/2587345/javascript-date-parse
        var parts = date_string.match(/(\d+)/g);
        // new Date(year, month [, date [, hours[, minutes[, seconds[, ms]]]]])
        return new Date(parts[0], parts[1] - 1, parts[2]); // months are 0-based
    }

    if (doc.doc_type == "XFormInstance") {//  && doc.xmlns == "http://dev.commcarehq.org/pact/dots_form") {
        if (doc.xmlns == 'http://code.javarosa.org/devicereport') {
            return;
        }
        emit (doc.received_on, null);
    }

}


