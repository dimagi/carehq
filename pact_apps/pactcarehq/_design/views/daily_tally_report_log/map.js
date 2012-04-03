function(doc) {
    //Check the daily submissions of the tally report and verify that it's already been sent once
    // !code util/dateparse.js

    //this is used for the calendar submits for per chw schedule DOTS visits whether or nto they're keeping with their schedule, hence, only dots forms.
    if (doc.doc_type == "SubmissionTallyLog") {
        var report_date = parse_date(doc.report_date);
        //return it in regular months, not zero indexed.
        emit([report_date.getFullYear(), report_date.getMonth()+1, report_date.getDate()], null);
    }
}