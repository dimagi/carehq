function(doc) {
	
	function padzero(n) {
		return n < 10 ? '0' + n : n;
	}
	function pad2zeros(n) {
		if (n < 100) {
			n = '0' + n;
		}
		if (n < 10) {
			n = '0' + n;
		}
		return n;     
	}
	function toISOString(d) {
		//source: http://williamsportwebdeveloper.com/cgi/wp/?p=503
		return d.getUTCFullYear() + '-' +  padzero(d.getUTCMonth() + 1) + '-' + padzero(d.getUTCDate()) + 'T' + padzero(d.getUTCHours()) + ':' +  padzero(d.getUTCMinutes()) + ':' + padzero(d.getUTCSeconds()) + '.' + pad2zeros(d.getUTCMilliseconds()) + 'Z';
	}
//	function fnToISO() {
//		var now = new Date();
//		alert(toISOString(now));
//	}
	
	function do_observation(doc, drug_arr, obs_dict) {
		if (drug_arr.length == 2 && drug_arr[0] !='unchecked') {
			obs_dict['adherence'] = drug_arr[0];
			obs_dict['method'] = drug_arr[1];
			//emit([doc._id, i.toString()], drug_obs);
			var use_date = new Date(doc.form['case']['update']['dots']['anchor']);
			emit(doc._id, obs_dict);
		}
	}
	
	function parse_date(date_string) {
	    if (!date_string) return new Date(1970,1,1);
	    // hat tip: http://stackoverflow.com/questions/2587345/javascript-date-parse    
	    var parts = date_string.match(/(\d+)/g);
	    // new Date(year, month [, date [, hours[, minutes[, seconds[, ms]]]]])
	    return new Date(parts[0], parts[1]-1, parts[2]); // months are 0-based
	}
	
	
	//function to emit all the dots observations into a format that's readable by the dotsview app
    if (doc.doc_type == "XFormInstance" && doc.xmlns == "http://dev.commcarehq.org/pact/dots_form") {
		var casedata = doc.form['case']['update'];		
		var dotsinfo = casedata['dots'];
		var anchor_date = new Date(dotsinfo['anchor']);
		//anchor_date.toGMTString
		var daily_data = dotsinfo['days'];
		var drop_note = true;
		
		for (var i = daily_data.length - 1; i >= 0; i--) {
			//iterate through each day (i)
			drug_day = daily_data[i];
			var observed_date = new Date(anchor_date.getTime() - (24*60*60*1000 * i));
			for (var j = 0; j < drug_day.length; j++) {
				//iterate through the drugs to get art status within a given day.  right now that's just 2
				var drug_obs = {};
				drug_obs['doc_id'] = doc._id;
				drug_obs['patient'] = doc.form['case']['case_id'];
				drug_obs['pact_id'] = doc.form['pact_id'];
				drug_obs['provider'] = doc.form['Meta']['username'];
				drug_obs['created_date'] = doc.form['Meta']['TimeStart'];
				drug_obs['completed_date'] = doc.form['Meta']['TimeEnd'];
				drug_obs['anchor_date'] = toISOString(anchor_date);
				
				if (i == daily_data.length - 1 && drop_note) {
					drug_obs['note'] = doc.form['notes'];
					drop_note = false;
				}
				var drug_info = drug_day[j];
				drug_obs['dose_number'] = j;
				drug_obs['total_doses'] = drug_info.length;
				
				drug_obs['observed_date'] = toISOString(observed_date);
				if (j == 0) {
					//non art is always zero'th
					drug_obs['is_art'] = false;
				}
				else {
					drug_obs['is_art'] = true;
				}
				for (var k = 0; k < drug_info.length; k++) {
					//within each drug, iterate through the "taken time", as according to frequency
					regimen_info = drug_info[k];
					do_observation(doc, regimen_info, drug_obs);
				}
			}
		}
	}
}

