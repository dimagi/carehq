function(doc) {
    //all submissions for DOTS notes by date
    //Parse the encounter date string.
    //note, that the dates are in 1 indexed months, so NO additions here.

    // !code util/dateparse.js

    if (doc.doc_type == "XFormInstance") {//  && doc.xmlns == "http://dev.commcarehq.org/pact/dots_form") {
        if (doc.form.encounter_date) {
            var edate = parse_date(doc.form.encounter_date);
        } else if (doc.form.note && doc.form.note.encounter_date) {
            var edate = parse_date(doc.form.note.encounter_date);
        } else {
            var edate = parse_date(doc.form['meta']['timeStart']);
        }

        var pact_id = "";
        if (doc.form.pact_id) {
            pact_id = doc.form.pact_id;
        }
        else if (doc.form.note.pact_id) {
            //only for encountern otes, so this is actualy ignored.
            pact_id = doc.form.note.pact_id;
        }

        //return it in regular months, not zero indexed.
        emit([pact_id, edate.getFullYear(), edate.getMonth() + 1, edate.getDate(), doc.xmlns], null);
    }
}


