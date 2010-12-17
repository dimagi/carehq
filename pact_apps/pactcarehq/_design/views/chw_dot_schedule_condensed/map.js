function(doc) {
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
                    //username, day_of_week-> (pact_id, active_date)
                    var emission = {};
                    emission['day_of_week'] = j;
                    emission['pact_id'] = doc.pact_id;
                    emission['active_date'] = schedule.started;
                    emission['ended_date'] = schedule.ended;
                    emission['schedule_index'] = i;
                    emit (username, emission);
                }
            }
		}
	}
}