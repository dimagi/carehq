function(doc) {
    //key = doc id
    if (doc.doc_type == "CaseDoc")
        emit(doc.django_id, null);
}