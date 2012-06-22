function (doc) {

    // !code util/dateparse.js

    if (doc.form.encounter_date) {
        var edate = parse_date(doc.form.encounter_date);
    } else if (doc.form.note && doc.form.note.encounter_date) {
        var edate = parse_date(doc.form.note.encounter_date);
    } else {
        var edate = parse_date(doc.form['meta']['timeStart']);
    }

    if (doc.doc_type == "XFormInstance" && doc.form.meta !== undefined) {
        emit([doc.form.meta.username, edate.getFullYear(), edate.getMonth() + 1, edate.getDate()],  null);
    }
}