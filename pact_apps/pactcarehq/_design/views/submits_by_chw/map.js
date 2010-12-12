function(doc) {
    //Parse the encounter date string.
    //note, that the dates are in 1 indexed months, so NO additions here.
    function get_user_id(xform_doc) {
        if (xform_doc.Meta) return xform_doc.Meta.username;
    }

    if (doc.doc_type == "XFormInstance") {
        emit(get_user_id(doc.form), doc);
    }
}