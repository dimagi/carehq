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

    if (doc.doc_type == "XFormInstance" && doc.xmlns == "http://shine.commcarehq.org/bloodwork/entry") {
        //use pact bloodwork for now as the test form while we figure out what else is going on
        var keys = getkeys(doc._attachments);
        if (keys.length > 1) {
            emit(doc._id, null);
        }
    }
}