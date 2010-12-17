function(doc) {
    if (doc.doc_type == "XFormInstance" && doc.form.case !== undefined) {
        emit(doc.form.case.case_id, null);
    }
}