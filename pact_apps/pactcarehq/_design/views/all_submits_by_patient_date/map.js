function(doc) {
    //all submissions for DOTS notes by date
    //Parse the encounter date string.
    //note, that the dates are in 1 indexed months, so NO additions here.
    function parse_date(date_string) {
        if (!date_string) return new Date(1970,1,1);
        // hat tip: http://stackoverflow.com/questions/2587345/javascript-date-parse
        var parts = date_string.match(/(\d+)/g);
        // new Date(year, month [, date [, hours[, minutes[, seconds[, ms]]]]])
        return new Date(parts[0], parts[1]-1, parts[2]); // months are 0-based
    }

    if (doc.doc_type == "XFormInstance"  && doc.xmlns == "http://dev.commcarehq.org/pact/dots_form") {
        if (doc.form.encounter_date) {
            var edate = parse_date(doc.form.encounter_date);
        } else if (doc.form.note && doc.form.note.encounter_date) {
            var edate = parse_date(doc.form.note.encounter_date);
        }

        var pact_id = "";
        if (doc.form.pact_id) {
	    	pact_id=doc.form.pact_id;
    	}
	    else if (doc.form.note.pact_id) {
            //only for encountern otes, so this is actualy ignored.
		    pact_id = doc.form.note.pact_id;
    	}

        //return it in regular months, not zero indexed.
        emit([pact_id, edate.getFullYear(), edate.getMonth()+1, edate.getDate(), doc.xmlns], null);
    }
}


