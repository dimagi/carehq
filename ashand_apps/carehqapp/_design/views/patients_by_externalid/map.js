function (doc) {
    if (doc.doc_type == "CarehqPatient")  {
        emit (doc.study_id, null);
    }
}