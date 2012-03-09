function(doc) {
    //Check the daily submissions of the tally report and verify that it's already been sent once
    function parse_date(date_string) {
        if (!date_string) return new Date(1970,1,1);
        // hat tip: http://stackoverflow.com/questions/2587345/javascript-date-parse
        var parts = date_string.match(/(\d+)/g);
        // new Date(year, month [, date [, hours[, minutes[, seconds[, ms]]]]])
        return new Date(parts[0], parts[1]-1, parts[2]); // months are 0-based
    }

    //this is used for the calendar submits for per chw schedule DOTS visits whether or nto they're keeping with their schedule, hence, only dots forms.
    if (doc.doc_type == "SubmissionTallyLog") {
        var report_date = parse_date(doc.report_date);
        //return it in regular months, not zero indexed.
        emit([report_date.getFullYear(), report_date.getMonth()+1, report_date.getDate()], null);
    }
}