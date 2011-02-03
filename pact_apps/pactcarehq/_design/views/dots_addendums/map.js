function(doc) {
    //function to emit all the dots observations into a format that's readable by the dotsview app
    if (doc.doc_type == "CObservationAddendum") {
        //we want to emit two classes of keys
        //1:  raw addendums
        emit(['addendum_group', 'created', doc.created_date], null);
        emit(['addendum_group', 'observed_date', doc.observed_date], null);
        //2:  same output as dots_observations: [pact_id, 'observe_date', date.year, date.month, date.day]
        for (var i = 0; i < doc.art_observations.length; i++) {
            var obs = doc.art_observations[i];
            var anchor_date = new Date(obs.anchor_date);
            var observe_date = new Date(obs.observed_date);

            emit([obs.pact_id, 'anchor_date', anchor_date.getFullYear(), anchor_date.getMonth() + 1, anchor_date.getDate()], obs);
            emit([obs.pact_id, 'observe_date', observe_date.getFullYear(), observe_date.getMonth() + 1, observe_date.getDate()], eval(uneval(obs)));
            emit([observe_date.getFullYear(), observe_date.getMonth() + 1, observe_date.getDate()], eval(uneval(obs)));
        }
    }
}
