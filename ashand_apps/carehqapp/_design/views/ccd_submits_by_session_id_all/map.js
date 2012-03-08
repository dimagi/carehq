function (doc) {
    if (doc['doc_type'] == "XFormInstance" || doc['doc_type'] == 'XFormDuplicate') {
        if (doc.xmlns == 'urn:hl7-org:v3') {
            emit([doc.form['id']['@root'], doc['doc_type']], null);
        }
    }
}