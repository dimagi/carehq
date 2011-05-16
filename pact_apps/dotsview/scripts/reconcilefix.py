from dotsview.models.couchmodels import CObservation, CObservationAddendum, ADDENDUM_NOTE_STRING


map_function = """
function(doc) {
    //function to emit all the dots observations into a format that's readable by the dotsview app

	function parse_date(date_string) {
	    if (!date_string) return new Date(1970,1,1);
	    // hat tip: http://stackoverflow.com/questions/2587345/javascript-date-parse
	    var parts = date_string.match(/(\d+)/g);
	    // new Date(year, month [, date [, hours[, minutes[, seconds[, ms]]]]])
	    return new Date(parts[0], parts[1]-1, parts[2]); // months are 0-based, subtract fromour encoutner date
	}


    if (doc.doc_type == "CObservationAddendum") {
        //we want to emit two classes of keys
        //1:  raw addendums
        emit(['addendum_group', 'created', doc.created_date], null);
        emit(['addendum_group', 'observed_date', doc.observed_date], null);
        //2:  same output as dots_observations: [pact_id, 'observe_date', date.year, date.month, date.day]
        for (var i = 0; i < doc.art_observations.length; i++) {
            var obs = doc.art_observations[i];
            var anchor_date = parse_date(obs.anchor_date);
            var observe_date = parse_date(obs.observed_date);

            emit([obs.pact_id, 'anchor_date', anchor_date.getFullYear(), anchor_date.getMonth() + 1, anchor_date.getDate()], obs);
            emit([obs.pact_id, 'observe_date', observe_date.getFullYear(), observe_date.getMonth() + 1, observe_date.getDate()], eval(uneval(obs)));
            emit([observe_date.getFullYear(), observe_date.getMonth() + 1, observe_date.getDate()], eval(uneval(obs)));
        }

        for (var i = 0; i < doc.nonart_observations.length; i++) {
            var obs = doc.nonart_observations[i];
            var anchor_date = parse_date(obs.anchor_date);
            var observe_date = parse_date(obs.observed_date);

            emit([obs.pact_id, 'anchor_date', anchor_date.getFullYear(), anchor_date.getMonth() + 1, anchor_date.getDate()], obs);
            emit([obs.pact_id, 'observe_date', observe_date.getFullYear(), observe_date.getMonth() + 1, observe_date.getDate()], eval(uneval(obs)));
            emit([observe_date.getFullYear(), observe_date.getMonth() + 1, observe_date.getDate()], eval(uneval(obs)));
        }
    }
}
"""

def run():

    observations = CObservationAddendum.view('pactcarehq/dots_addendums', startkey=['addendum_group', 'created', '\x00'], endkey = ['addendum_group', 'created',u'\ufff0'], include_docs=True).all()
    for obs in observations:
        print obs
        #if it's off a document
        print obs['observed_date']
        for o in obs.art_observations:
            o.is_reconciliation=True
            if o.day_note == ADDENDUM_NOTE_STRING:
                o.day_note = ''
            #o.save()
        for o in obs.nonart_observations:
            o.is_reconciliation=True
            if o.day_note == ADDENDUM_NOTE_STRING:
                o.day_note = ''
            #o.save()
        #print len(obs.art_observations)
        #print len(obs.nonart_observations)

        #obs.is_reconciled=True
        obs.save()
