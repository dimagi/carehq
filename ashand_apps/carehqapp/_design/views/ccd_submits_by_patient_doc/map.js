function (doc) {
    if (doc['doc_type'] == "XFormInstance") {
        if (doc.xmlns == 'urn:hl7-org:v3') {
            //datetime.strptime(submission.form['author']['time']['@value'][0:8], '%Y%m%d'
            var timestring = doc.form['author']['time']['@value'];
            var year = parseInt(timestring.substring(0,4));
            var month = parseInt(timestring.substring(4,6));
            var day = parseInt(timestring.substring(6,8));

            emit([doc.form['recordTarget']['patientRole']['id'][1]['@extension'], year, month, day], null);
        }
    }
}