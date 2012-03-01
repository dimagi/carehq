function (doc) {
    if (doc['doc_type'] == "XFormInstance") {
        if (doc.xmlns == 'urn:hl7-org:v3') {
            emit(doc.form['id']['@root'], null);
        }
    }
}