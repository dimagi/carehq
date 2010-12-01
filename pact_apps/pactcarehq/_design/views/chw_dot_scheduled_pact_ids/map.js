function(doc) {

    //return a distilled list of JUST the pact ids that a dots chw knows about on their schedule.
    //with some more sophistication, we might put a date range on this, but for now, it'll do it ALL historically.
	var days = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday'];
	if (doc.doc_type == "CPatient") {
		var schedules = doc.weekly_schedule;
		for (var i = 0; i < schedules.length; i++) {
			var schedule = schedules[i];
            for (var j = 0; j < days.length; j++) {
                var username = schedule[days[j]];
                if (username == null)  {
                    continue;
                }
                else {
                    //this might need more sophistication
                    //var emission = {};
                    //emission['pact_id'] = doc.pact_id;
                    //emission['active_date'] = schedule.started;
                    //emission['day_of_week'] = j;
                    //emission['schedule_index'] = i;
                    //emission['ended_date'] = schedule.ended;
                    emit (username, doc.pact_id);
                }
            }
		}
	}
}