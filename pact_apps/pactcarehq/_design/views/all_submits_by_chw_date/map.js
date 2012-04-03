function (doc) {

    // !code util/dateparse.js

    if (doc.form.encounter_date) {
        var edate = parse_date(doc.form.encounter_date);
    } else if (doc.form.note && doc.form.note.encounter_date) {
        var edate = parse_date(doc.form.note.encounter_date);
    } else {
        var edate = parse_date(doc.form['Meta']['TimeStart']);
    }

    if (doc.doc_type == "XFormInstance" && doc.form.Meta !== undefined) {
        emit([doc.form.Meta.username, edate.getFullYear(), edate.getMonth() + 1, edate.getDate()],  null);
    }
}