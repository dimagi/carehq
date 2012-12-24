function (doc) {
    //all submissions for DOTS notes by date
    //Parse the encounter date string.
    //note, that the dates are in 1 indexed months, so NO additions here.

    // !code util/dateparse.js

    if (doc.doc_type == "XFormInstance")
        if (doc.form.case) {
            if (doc.form.case['@case_id']) {
                emit(doc.form.case['@case_id'], null);
            } else if (doc.form.case['case_id']) {
                emit(doc.form.case['case_id'], null);
            }

        }
        else {
            emit("no case", null);
        }
}


