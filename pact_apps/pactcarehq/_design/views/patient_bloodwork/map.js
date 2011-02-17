function(doc) {
    if (doc.doc_type == "XFormInstance" && doc.xmlns == "http://dev.commcarehq.org/pact/progress_note" && doc.form.Meta !== undefined) {
        if (doc.form.note.bwresults != "") {
            if (doc.form.note.bwresults.bw.length != undefined) {
                //this is hacky because we should check .constructor == Array, but it doesn't seem to work here for some reason.
                for (var i = 0; i < doc.form.note.bwresults.bw.length; i++) {
                    if (doc.form.note.bwresults.bw[i].tests != "") {
                        emit(doc.form.note.pact_id, doc.form.note.bwresults.bw[i]);
                    }
                }
            }
            else {
                if (doc.form.note.bwresults.bw.tests != "") {
                    emit(doc.form.note.pact_id, doc.form.note.bwresults.bw);
                }
            }
        }
    } else if(doc.doc_type == "XFormInstance" && doc.xmlns == "http://dev.commcarehq.org/pact/bloodwork") {
        if (doc.form.results.bw.length != undefined) {
            //it's an array
            for (var i = 0; i < doc.form.results.bw.length; i++) {
                emit (doc.form.pact_id, doc.form.results.bw[i]);       
            }
        }
        else {
            if (doc.form.results.bw.tests != "") {
                emit (doc.form.pact_id, doc.form.results.bw);
            }
        }
    }

}