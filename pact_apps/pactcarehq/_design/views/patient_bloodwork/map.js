function(doc) {
    if (doc.doc_type == "XFormInstance" && doc.xmlns == "http://dev.commcarehq.org/pact/progress_note" && doc.form.Meta !== undefined) {
        if (doc.form.note.bwresults != "") {
            if (doc.form.note.bwresults.bw.length != undefined) {
                //this is hacky because we should check .constructor == Array, but it doesn't seem to work here for some reason.
                for (var i = 0; i < doc.form.note.bwresults.bw.length; i++) {
                    emit(doc.form.note.pact_id, doc.form.note.bwresults.bw[i]);
                }
            }
            else {
                emit(doc.form.note.pact_id, doc.form.note.bwresults.bw);
            }
        }
    }
}