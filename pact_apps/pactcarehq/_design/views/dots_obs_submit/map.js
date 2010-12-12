function(doc) {
	//this indexes by the observed date the dots observations
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
	
	function do_observation(doc, observe_date, drug_arr, obs_dict) {
		if (drug_arr.length >= 2 && drug_arr[0] != 'unchecked') {
			obs_dict['adherence'] = drug_arr[0];
			obs_dict['method'] = drug_arr[1];
            if (drug_arr.length == 3) {
				obs_dict['day_note'] = drug_arr[2];
			}
			emit(doc._id, obs_dict);
			//var use_date = new Date(doc.form['case']['update']['dots']['anchor']);
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
        if (casedata['dots'] != undefined) {
            var anchor_date = new Date(casedata['dots']['anchor']);
            var daily_data = casedata['dots']['days'];
            var drop_note = true;

            for (var i = 0; i < daily_data.length; i+=1) {
                //iterate through each day = i
                var day_delta = daily_data.length-1-i;
                var drug_classes = daily_data[i];
                //var observed_date = new Date(anchor_date.getTime() - (24*3600*1000 * i));
                var observed_date = new Date(casedata['dots']['anchor']);
                observed_date.setDate(anchor_date.getDate()-day_delta);
                for (var j = 0; j < drug_classes.length; j+=1) {
                    //iterate through the drugs to get art status within a given day.  right now that's just 2
                    var dispenses = drug_classes[j]; //right now just 2 elements[art, nonart]
                    var is_art = false;
                    if (j == 0) {
                        //non art drug is always zero'th
                        is_art = false;
                    }
                    else {
                        is_art = true;
                    }
                    var note = '';
                    if (i == daily_data.length - 1 && drop_note) {
                        //if this is the first element at the anchor date, put the note of the xform in here.
                        note = doc.form['notes'];
                        drop_note = false;
                    }

                    for (var drug_freq = 0; drug_freq < dispenses.length; drug_freq+=1) {
                        //within each drug, iterate through the "taken time", as according to frequency
                        //populate the rest of the information
                        //create the dictionary to be emitted
                        var drug_obs = {};
                        drug_obs['doc_id'] = doc._id;
                        drug_obs['patient'] = doc.form['case']['case_id'];
                        drug_obs['pact_id'] = doc.form['pact_id'];
                        drug_obs['provider'] = doc.form['Meta']['username'];
                        drug_obs['created_date'] = doc.form['Meta']['TimeStart'];
                        drug_obs['completed_date'] = doc.form['Meta']['TimeEnd'];
                        drug_obs['anchor_date'] = toISOString(anchor_date);
                        drug_obs['day_index'] = day_delta;
                        drug_obs['is_art'] = is_art;
                        drug_obs['note'] = note;
                        drug_obs['total_doses'] = dispenses.length;
                        drug_obs['observed_date'] = toISOString(observed_date);
                        drug_obs['dose_number'] = drug_freq;
                        do_observation(doc, observed_date, dispenses[drug_freq], drug_obs);
                    }
                }
            }
        }
	}
}

