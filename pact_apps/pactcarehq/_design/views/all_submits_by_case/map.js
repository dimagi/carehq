function(doc) {
    if (doc.doc_type == "XFormInstance") {
        emit(doc.form.case.case_id, doc);
    }
}