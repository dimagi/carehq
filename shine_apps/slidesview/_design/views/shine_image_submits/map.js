function(doc) {
    //view to see all patients that are DOT patients.
    function getkeys(obj) {
        var keys = [];
        for (var key in obj) {
            if (obj.hasOwnProperty(key)) { //to be safe
                keys.push(key);
            }
        }
        return keys;
    }

    if (doc.doc_type == "XFormInstance" && doc.xmlns.substring(0, 28) == "http://shine.commcarehq.org/") {
        //use pact bloodwork for now as the test form while we figure out what else is going on
        var keys = getkeys(doc._attachments);
        for (var i = 0; i < keys.length; i++) {
            if (keys[i] != 'form.xml') {
                //emit the doc id because we're scanning by cases, which has submission ids.
                //for each doc, extract the submission's attachments.
                emit(doc._id, [doc.xmlns, keys[i]]);
            }
        }

    }
}