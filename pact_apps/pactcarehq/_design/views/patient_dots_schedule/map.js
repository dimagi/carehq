function(doc) {
    //this view emits the pact_id of the patient's schedule, and the EXPIRATION date of the schedule in question
    //when doing queries you will set the key for the date you want to check the validity for.  If the expiration is null, then it's valid?
	if (doc.doc_type == "CPatient") {
		var schedules = doc.weekly_schedule;
		for (var i = 0; i < schedules.length; i++) {
			var schedule = schedules[i];
            emit(doc.pact_id, schedule);
		}
	}
}