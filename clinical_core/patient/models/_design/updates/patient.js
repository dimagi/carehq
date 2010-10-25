function(doc, req) {
    var xform = new XML(req.body);
    var resp =  {"headers" : {"Content-Type" : "application/xml"},
                 "body" : xform};
    return [doc, resp];
}