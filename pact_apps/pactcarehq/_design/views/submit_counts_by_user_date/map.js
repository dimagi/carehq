function(doc) {
    // parse a date in yyyy-mm-dd format
    function parse_date(date_string) {
        if (!date_string) return new Date(1970,1,1);
        // hat tip: http://stackoverflow.com/questions/2587345/javascript-date-parse
        var parts = date_string.match(/(\d+)/g);
        // new Date(year, month [, date [, hours[, minutes[, seconds[, ms]]]]])
        return new Date(parts[0], parts[1]-1, parts[2]); // months are 0-based
    }

    function get_encounter_date(xform_doc) {
        function get_date_string(xform_doc) {
            // check some expected places for a date
            if (xform_doc.encounter_date) return xform_doc.encounter_date;
            if (xform_doc.note && xform_doc.note.encounter_date) return xform_doc.note.encounter_date;
            if (xform_doc.Meta && xform_doc.Meta.TimeEnd) return xform_doc.Meta.TimeEnd;
            if (xform_doc.Meta && xform_doc.Meta.TimeStart) return xform_doc.Meta.TimeStart;
            return null;
        }
        return parse_date(get_date_string(xform_doc));
    }

    function get_user_id(xform_doc) {
        if (xform_doc.Meta) return xform_doc.Meta.username;
    }
    if (doc["doc_type"] == "XFormInstance" && get_user_id(doc.form) != null) {
        date = get_encounter_date(doc.form);
        if (!date) {
            date = Date();
        }
        //when we do a Date, always from javascript set it to 1 indexed.
        emit([get_user_id(doc.form), date.getFullYear(), date.getMonth()+1, date.getDate(), doc["xmlns"]], 1);
    }
}
