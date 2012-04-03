function(doc) {
//chw_dashboard
//returns an array of key: chw_username: [count, last_pact_id, last_xmlns, received_on]

    // !code util/dateparse.js

    function bw_array_sort(a, b) {
        //doing reverse date order
        var datea = parse_date(a['test_date']);
        var dateb = parse_date(b['test_date']);

        if (datea > dateb) {
            return -1;
        } else if (datea < dateb) {
            return 1;
        } else {
            return 0;
        }
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
        if (xform_doc.Meta && xform_doc.Meta.username) return xform_doc.Meta.username;
        if (xform_doc.Meta && xform_doc.Meta.chw_id) return xform_doc.Meta.chw_id;
    }

    //Parse the encounter date string.
    //note, that the dates are in 1 indexed months, so NO additions here.

    if (doc.doc_type == "XFormInstance" && doc.xmlns != "http://code.javarosa.org/devicereport") {
        //map 1:  XForm Information regarding bloodwork and submission counts
        if (doc.form.encounter_date) {
            var edate = parse_date(doc.form.encounter_date);
        } else if (doc.form.note && doc.form.note.encounter_date) {
            var edate = parse_date(doc.form.note.encounter_date);
        }

        //return it in regular months, not zero indexed.
        if (doc.form.pact_id) {
            var pact_id = doc.form.pact_id;
        } else if (doc.form.note && doc.form.note.pact_id) {
            var pact_id = doc.form.note.pact_id;
        }
        var ret_dict = {};
        ret_dict['count'] = 1;
        ret_dict['encounter_date'] = get_encounter_date(doc.form);
        ret_dict['doc_id'] = doc._id;
        ret_dict['pact_id'] = pact_id;
        ret_dict['last_xmlns'] = doc.xmlns;
        ret_dict['last_received'] = doc.received_on;

        emit(get_user_id(doc.form), ret_dict);
    }
}


