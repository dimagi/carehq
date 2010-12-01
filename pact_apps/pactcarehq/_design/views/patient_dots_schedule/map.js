function(doc) {
    //this view emits the pact_id of the patient's schedule, and the EXPIRATION date of the schedule in question
    //when doing queries you will set the key for the date you want to check the validity for.  If the expiration is null, then it's valid?
//
//    function padzero(n) {
//		return n < 10 ? '0' + n : n;
//	}
//	function pad2zeros(n) {
//		if (n < 100) {
//			n = '0' + n;
//		}
//		if (n < 10) {
//			n = '0' + n;
//		}
//		return n;
//	}
//
//    function toSimpleISOString(d) {
//		//source: http://williamsportwebdeveloper.com/cgi/wp/?p=503
//		//return d.getUTCFullYear() + '-' +  padzero(d.getUTCMonth() + 1) + '-' + padzero(d.getUTCDate()) + 'T' + padzero(d.getUTCHours()) + ':' +  padzero(d.getUTCMinutes()) + ':' + padzero(d.getUTCSeconds()) + '.' + pad2zeros(d.getUTCMilliseconds()) + 'Z';
//        return d.getUTCFullYear() + '-' +  padzero(d.getUTCMonth() + 1) + '-' + padzero(d.getUTCDate());
//	}
//
//    function parse_date(date_string) {
//	    if (!date_string) return new Date(1970,1,1);
//	    // hat tip: http://stackoverflow.com/questions/2587345/javascript-date-parse
//	    var parts = date_string.match(/(\d+)/g);
//	    // new Date(year, month [, date [, hours[, minutes[, seconds[, ms]]]]])
//	    return new Date(parts[0], parts[1]-1, parts[2]); // months are 0-based
//	}

	if (doc.doc_type == "CPatient") {
		var schedules = doc.weekly_schedule;
		for (var i = 0; i < schedules.length; i++) {
			var schedule = schedules[i];
            emit(doc.pact_id, schedule);
//            if (schedule.ended == null) {
//                var nowdate = new Date();
//                emit ([doc.pact_id, toSimpleISOString(nowdate), toSimpleISOString(parse_date(schedule.started))], schedule);
//            } else {
//                emit ([doc.pact_id, toSimpleISOString(parse_date(schedule.ended)), toSimpleISOString(parse_date(schedule.started))], schedule);
//            }
		}
	}
}