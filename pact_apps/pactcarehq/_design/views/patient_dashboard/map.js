function(doc) {
//returns an array of key: pact_id: [count, encounter_date, doc_id, chw_id, xmlns, received_on]


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
    function parse_date(date_string) {
        if (!date_string) return new Date(1970, 1, 1);
        // hat tip: http://stackoverflow.com/questions/2587345/javascript-date-parse
        var parts = date_string.match(/(\d+)/g);
        // new Date(year, month [, date [, hours[, minutes[, seconds[, ms]]]]])
        return new Date(parts[0], parts[1] - 1, parts[2]); // months are 0-based
    }
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
        ret_dict['chw_id'] = get_user_id(doc.form);
        ret_dict['last_xmlns'] = doc.xmlns;
        ret_dict['last_received'] = doc.received_on;

        //check to see if there's a bloodwork to emit
        if(doc.form.note) {
            if (doc.form.note.bwresults != "") {
                if (doc.form.note.bwresults.bw.length != undefined) {
                    //this is hacky because we should check .constructor == Array, but it doesn't seem to work here for some reason.
                    //so the bw is an array, let's sort it
                    doc.form.note.bwresults.bw.sort(bw_array_sort)
                    ret_dict['last_bloodwork'] = doc.form.note.bwresults.bw[0];
                }
                else {
                    ret_dict['last_bloodwork'] = doc.form.note.bwresults.bw;
                }
            }
        }
        emit(pact_id, ret_dict);
    }

    else if (doc.doc_type == "CPatient") {
        //map 2:  patient information to reduce lookup costs on the patient dashbaord
        var ret_dict = {};
        var pat_dict = {};
        ret_dict['patient_doc'] = pat_dict //this kills the reduce limit
        pat_dict['pact_id'] = doc.pact_id
        pat_dict['django_uuid'] = doc.django_uuid
        pat_dict['last_name'] = doc.last_name
        pat_dict['first_name'] = doc.first_name
        pat_dict['arm'] = doc.arm
        pat_dict['primary_hp'] = doc.primary_hp
        emit (doc.pact_id, ret_dict)


    }
}


